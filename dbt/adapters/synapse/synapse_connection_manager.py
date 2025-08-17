import struct
import time
from itertools import chain, repeat
from typing import Callable, Dict, Mapping, Optional

import pyodbc
from azure.core.credentials import AccessToken
from azure.identity import AzureCliCredential, DefaultAzureCredential, EnvironmentCredential
from dbt.adapters.contracts.connection import Connection, ConnectionState
from dbt.adapters.events.logging import AdapterLogger
from dbt.adapters.fabric import FabricConnectionManager, __version__
from dbt.adapters.fabric.fabric_credentials import FabricCredentials

AZURE_CREDENTIAL_SCOPE = "https://database.windows.net//.default"
_TOKEN: Optional[AccessToken] = None
AZURE_AUTH_FUNCTION_TYPE = Callable[[FabricCredentials], AccessToken]

logger = AdapterLogger("fabric")


def convert_bytes_to_mswindows_byte_string(value: bytes) -> bytes:
    """
    Convert bytes to a Microsoft windows byte string.

    Parameters
    ----------
    value : bytes
        The bytes.

    Returns
    -------
    out : bytes
        The Microsoft byte string.
    """
    encoded_bytes = bytes(chain.from_iterable(zip(value, repeat(0))))
    return struct.pack("<i", len(encoded_bytes)) + encoded_bytes


def convert_access_token_to_mswindows_byte_string(token: AccessToken) -> bytes:
    """
    Convert an access token to a Microsoft windows byte string.

    Parameters
    ----------
    token : AccessToken
        The token.

    Returns
    -------
    out : bytes
        The Microsoft byte string.
    """
    value = bytes(token.token, "UTF-8")
    return convert_bytes_to_mswindows_byte_string(value)


def get_cli_access_token(credentials: FabricCredentials) -> AccessToken:
    """
    Get an Azure access token using the CLI credentials

    First login with:

    ```bash
    az login
    ```

    Parameters
    ----------
    credentials: FabricConnectionManager
        The credentials.

    Returns
    -------
    out : AccessToken
        Access token.
    """
    _ = credentials
    token = AzureCliCredential().get_token(
        AZURE_CREDENTIAL_SCOPE, timeout=getattr(credentials, "login_timeout", None)
    )
    return token


def get_auto_access_token(credentials: FabricCredentials) -> AccessToken:
    """
    Get an Azure access token automatically through azure-identity

    Parameters
    -----------
    credentials: FabricCredentials
        Credentials.

    Returns
    -------
    out : AccessToken
        The access token.
    """
    token = DefaultAzureCredential().get_token(
        AZURE_CREDENTIAL_SCOPE, timeout=getattr(credentials, "login_timeout", None)
    )
    return token


def get_environment_access_token(credentials: FabricCredentials) -> AccessToken:
    """
    Get an Azure access token by reading environment variables

    Parameters
    -----------
    credentials: FabricCredentials
        Credentials.

    Returns
    -------
    out : AccessToken
        The access token.
    """
    token = EnvironmentCredential().get_token(
        AZURE_CREDENTIAL_SCOPE, timeout=getattr(credentials, "login_timeout", None)
    )
    return token


AZURE_AUTH_FUNCTIONS: Mapping[str, AZURE_AUTH_FUNCTION_TYPE] = {
    "cli": get_cli_access_token,
    "auto": get_auto_access_token,
    "environment": get_environment_access_token,
}


def get_pyodbc_attrs_before(credentials: FabricCredentials) -> Dict:
    """
    Get the pyodbc attrs before.

    Parameters
    ----------
    credentials : FabricCredentials
        Credentials.

    Returns
    -------
    out : Dict
        The pyodbc attrs before.

    Source
    ------
    Authentication for SQL server with an access token:
    https://docs.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver15#authenticating-with-an-access-token
    """
    global _TOKEN
    attrs_before: Dict
    MAX_REMAINING_TIME = 300

    authentication = str(credentials.authentication).lower()
    if authentication in AZURE_AUTH_FUNCTIONS:
        time_remaining = (_TOKEN.expires_on - time.time()) if _TOKEN else MAX_REMAINING_TIME

        if _TOKEN is None or (time_remaining < MAX_REMAINING_TIME):
            azure_auth_function = AZURE_AUTH_FUNCTIONS[authentication]
            _TOKEN = azure_auth_function(credentials)

        token_bytes = convert_access_token_to_mswindows_byte_string(_TOKEN)
        sql_copt_ss_access_token = 1256  # see source in docstring
        attrs_before = {sql_copt_ss_access_token: token_bytes}
    else:
        attrs_before = {}

    return attrs_before


def bool_to_connection_string_arg(key: str, value: bool) -> str:
    """
    Convert a boolean to a connection string argument.

    Parameters
    ----------
    key : str
        The key to use in the connection string.
    value : bool
        The boolean to convert.

    Returns
    -------
    out : str
        The connection string argument.
    """
    return f'{key}={"Yes" if value else "No"}'


class SynapseConnectionManager(FabricConnectionManager):
    TYPE = "synapse"
    TOKEN = None

    @classmethod
    def open(cls, connection: Connection) -> Connection:
        if connection.state == ConnectionState.OPEN:
            logger.debug("Connection is already open, skipping open.")
            return connection

        credentials = cls.get_credentials(connection.credentials)

        con_str = [f"DRIVER={{{credentials.driver}}}"]

        if "\\" in credentials.host:
            # If there is a backslash \ in the host name, the host is a
            # SQL Server named instance. In this case then port number has to be omitted.
            con_str.append(f"SERVER={credentials.host}")
        else:
            con_str.append(f"SERVER={credentials.host}")

        con_str.append(f"Database={credentials.database}")

        assert credentials.authentication is not None

        if "ActiveDirectory" in credentials.authentication:
            con_str.append(f"Authentication={credentials.authentication}")

            if credentials.authentication == "ActiveDirectoryPassword":
                con_str.append(f"UID={{{credentials.UID}}}")
                con_str.append(f"PWD={{{credentials.PWD}}}")
            if credentials.authentication == "ActiveDirectoryServicePrincipal":
                con_str.append(f"UID={{{credentials.client_id}}}")
                con_str.append(f"PWD={{{credentials.client_secret}}}")
            elif credentials.authentication == "ActiveDirectoryInteractive":
                con_str.append(f"UID={{{credentials.UID}}}")

        elif credentials.windows_login:
            con_str.append("trusted_connection=Yes")
        elif credentials.authentication == "sql":
            con_str.append(f"UID={{{credentials.UID}}}")
            con_str.append(f"PWD={{{credentials.PWD}}}")

        # https://docs.microsoft.com/en-us/sql/relational-databases/native-client/features/using-encryption-without-validation?view=sql-server-ver15
        assert credentials.encrypt is not None
        assert credentials.trust_cert is not None

        con_str.append(bool_to_connection_string_arg("encrypt", credentials.encrypt))
        con_str.append(
            bool_to_connection_string_arg("TrustServerCertificate", credentials.trust_cert)
        )

        plugin_version = __version__.version
        application_name = f"dbt-{credentials.type}/{plugin_version}"
        con_str.append(f"APP={application_name}")

        try:
            if int(credentials.retries) > 0:
                con_str.append(f"ConnectRetryCount={credentials.retries}")

        except Exception as e:
            logger.debug(
                "Retry count should be integer value. Skipping retries in the connection string.",
                str(e),
            )

        con_str_concat = ";".join(con_str)

        index = []
        for i, elem in enumerate(con_str):
            if "pwd=" in elem.lower():
                index.append(i)

        if len(index) != 0:
            con_str[index[0]] = "PWD=***"

        con_str_display = ";".join(con_str)

        retryable_exceptions = [  # https://github.com/mkleehammer/pyodbc/wiki/Exceptions
            pyodbc.InternalError,  # not used according to docs, but defined in PEP-249
            pyodbc.OperationalError,
        ]

        if credentials.authentication.lower() in AZURE_AUTH_FUNCTIONS:
            # Temporary login/token errors fall into this category when using AAD
            retryable_exceptions.append(pyodbc.InterfaceError)

        def connect():
            logger.debug(f"Using connection string: {con_str_display}")

            attrs_before = get_pyodbc_attrs_before(credentials)
            handle = pyodbc.connect(
                con_str_concat,
                attrs_before=attrs_before,
                autocommit=True,
                timeout=credentials.login_timeout,
            )
            handle.timeout = credentials.query_timeout
            logger.debug(f"Connected to db: {credentials.database}")
            return handle

        return cls.retry_connection(
            connection,
            connect=connect,
            logger=logger,
            retry_limit=credentials.retries,
            retryable_exceptions=retryable_exceptions,
        )

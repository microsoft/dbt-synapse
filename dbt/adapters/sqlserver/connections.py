from contextlib import contextmanager

import pyodbc
import os
import time
import struct
from itertools import chain, repeat

import dbt.exceptions
from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager
from azure.core.credentials import AccessToken
from azure.identity import AzureCliCredential, DefaultAzureCredential

from dbt.logger import GLOBAL_LOGGER as logger

from dataclasses import dataclass
from typing import Optional


AZURE_CREDENTIAL_SCOPE = "https://database.windows.net//.default"


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


def get_cli_access_token() -> AccessToken:
    """
    Get an Azure access token using the CLI credentials

    First login with:

    ```bash
    az login
    ```

    Returns
    -------
    out : AccessToken
        Access token.
    """
    token = AzureCliCredential().get_token(AZURE_CREDENTIAL_SCOPE)
    return token


def get_sp_access_token(
    tenant_id: str, client_id: str, client_secret: str
) -> AccessToken:
    """
    Get an Azure access token using the SP credentials.

    Parameters
    ----------
    tenant_id : str
        The tenant id.
    client_id : str
        The client id.
    client_secret :
        The client secret.
    """
    # bc DefaultAzureCredential will look in env variables
    os.environ["AZURE_TENANT_ID"] = tenant_id
    os.environ["AZURE_CLIENT_ID"] = client_id
    os.environ["AZURE_CLIENT_SECRET"] = client_secret

    token = DefaultAzureCredential().get_token(AZURE_CREDENTIAL_SCOPE)
    return token


@dataclass
class SQLServerCredentials(Credentials):
    driver: str
    host: str
    database: str
    schema: str
    port: Optional[int] = 1433
    UID: Optional[str] = None
    PWD: Optional[str] = None
    windows_login: Optional[bool] = False
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    # "sql", "ActiveDirectoryPassword" or "ActiveDirectoryInteractive", or
    # "ServicePrincipal"
    authentication: Optional[str] = "sql"
    encrypt: Optional[bool] = True
    trust_cert: Optional[bool] = True

    _ALIASES = {
        "user": "UID",
        "username": "UID",
        "pass": "PWD",
        "password": "PWD",
        "server": "host",
        "trusted_connection": "windows_login",
        "auth": "authentication",
        "app_id": "client_id",
        "app_secret": "client_secret",
        "TrustServerCertificate": "trust_cert",
    }

    @property
    def type(self):
        return "sqlserver"

    def _connection_keys(self):
        # return an iterator of keys to pretty-print in 'dbt debug'
        # raise NotImplementedError
        if self.windows_login is True:
            self.authentication = "Windows Login"

        return (
            "server",
            "database",
            "schema",
            "port",
            "UID",
            "client_id",
            "authentication",
            "encrypt",
            "trust_cert",
        )


class SQLServerConnectionManager(SQLConnectionManager):
    TYPE = "sqlserver"
    TOKEN = None

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except pyodbc.DatabaseError as e:
            logger.debug("Database error: {}".format(str(e)))

            try:
                # attempt to release the connection
                self.release()
            except pyodbc.Error:
                logger.debug("Failed to release connection!")
                pass

            raise dbt.exceptions.DatabaseException(str(e).strip()) from e

        except Exception as e:
            logger.debug(f"Error running SQL: {sql}")
            logger.debug("Rolling back transaction.")
            self.release()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise

            raise dbt.exceptions.RuntimeException(e)

    @classmethod
    def open(cls, connection):

        if connection.state == "open":
            logger.debug("Connection is already open, skipping open.")
            return connection

        credentials = connection.credentials

        try:
            con_str = []
            con_str.append(f"DRIVER={{{credentials.driver}}}")

            if "\\" in credentials.host:
                # if there is a backslash \ in the host name the host is a sql-server named instance
                # in this case then port number has to be omitted
                con_str.append(f"SERVER={credentials.host}")
            else:
                con_str.append(f"SERVER={credentials.host},{credentials.port}")

            con_str.append(f"Database={credentials.database}")

            type_auth = getattr(credentials, "authentication", "sql")

            if "ActiveDirectory" in type_auth:
                con_str.append(f"Authentication={credentials.authentication}")

                if type_auth == "ActiveDirectoryPassword":
                    con_str.append(f"UID={{{credentials.UID}}}")
                    con_str.append(f"PWD={{{credentials.PWD}}}")
                elif type_auth == "ActiveDirectoryInteractive":
                    con_str.append(f"UID={{{credentials.UID}}}")
                elif type_auth == "ActiveDirectoryIntegrated":
                    # why is this necessary???
                    con_str.remove("UID={None}")
                elif type_auth == "ActiveDirectoryMsi":
                    raise ValueError("ActiveDirectoryMsi is not supported yet")

            elif type_auth == "ServicePrincipal":
                app_id = getattr(credentials, "AppId", None)
                app_secret = getattr(credentials, "AppSecret", None)

            elif getattr(credentials, "windows_login", False):
                con_str.append(f"trusted_connection=yes")
            elif type_auth == "sql":
                con_str.append("Authentication=SqlPassword")
                con_str.append(f"UID={{{credentials.UID}}}")
                con_str.append(f"PWD={{{credentials.PWD}}}")

            if not getattr(credentials, "encrypt", False):
                con_str.append(f"Encrypt=yes")
            if not getattr(credentials, "trust_cert", False):
                con_str.append(f"TrustServerCertificate=yes")

            con_str_concat = ";".join(con_str)

            index = []
            for i, elem in enumerate(con_str):
                if "pwd=" in elem.lower():
                    index.append(i)

            if len(index) != 0:
                con_str[index[0]] = "PWD=***"

            con_str_display = ";".join(con_str)

            logger.debug(f"Using connection string: {con_str_display}")

            if type_auth != "ServicePrincipal":
                handle = pyodbc.connect(con_str_concat, autocommit=True)

            elif type_auth == "ServicePrincipal":

                # create token if it does not exist
                if cls.TOKEN is None:
                    tenant_id = getattr(credentials, "tenant_id", None)
                    client_id = getattr(credentials, "client_id", None)
                    client_secret = getattr(credentials, "client_secret", None)

                    token = get_sp_access_token(
                        tenant_id, client_id, client_secret
                    )
                    cls.TOKEN = convert_access_token_to_mswindows_byte_string(
                        token
                    )

                handle = pyodbc.connect(
                    con_str_concat,
                    attrs_before={1256: cls.TOKEN},
                    autocommit=True,
                )

            connection.state = "open"
            connection.handle = handle
            logger.debug(f"Connected to db: {credentials.database}")

        except pyodbc.Error as e:
            logger.debug(f"Could not connect to db: {e}")

            connection.handle = None
            connection.state = "fail"

            raise dbt.exceptions.FailedToConnectException(str(e))

        return connection

    def cancel(self, connection):
        logger.debug("Cancel query")
        pass

    def add_begin_query(self):
        # return self.add_query('BEGIN TRANSACTION', auto_begin=False)
        pass

    def add_commit_query(self):
        # return self.add_query('COMMIT TRANSACTION', auto_begin=False)
        pass

    def add_query(
        self, sql, auto_begin=True, bindings=None, abridge_sql_log=False
    ):

        connection = self.get_thread_connection()

        if auto_begin and connection.transaction_open is False:
            self.begin()

        logger.debug(
            'Using {} connection "{}".'.format(self.TYPE, connection.name)
        )

        with self.exception_handler(sql):
            if abridge_sql_log:
                logger.debug(
                    "On {}: {}....".format(connection.name, sql[0:512])
                )
            else:
                logger.debug("On {}: {}".format(connection.name, sql))
            pre = time.time()

            cursor = connection.handle.cursor()

            # pyodbc does not handle a None type binding!
            if bindings is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, bindings)

            logger.debug(
                "SQL status: {} in {:0.2f} seconds".format(
                    self.get_status(cursor), (time.time() - pre)
                )
            )

            return connection, cursor

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    @classmethod
    def get_status(cls, cursor):
        if cursor.rowcount == -1:
            status = "OK"
        else:
            status = str(cursor.rowcount)
        return status

    def execute(self, sql, auto_begin=True, fetch=False):
        _, cursor = self.add_query(sql, auto_begin)
        status = self.get_status(cursor)
        if fetch:
            table = self.get_result_from_cursor(cursor)
        else:
            table = dbt.clients.agate_helper.empty_table()
        return status, table

import mssql_python
from dbt.adapters.contracts.connection import Connection, ConnectionState
from dbt.adapters.events.logging import AdapterLogger
from dbt.adapters.fabric import FabricConnectionManager
from dbt.adapters.fabric.fabric_connection_manager import (
    bool_to_connection_string_arg,
    byte_array_to_datetime,
)

from dbt.adapters.synapse.synapse_credentials import SynapseCredentials

logger = AdapterLogger("synapse")

DATETIMEOFFSET_SQL_TYPE = -155


def braced(value: object) -> str:
    return "{" + str(value).replace("}", "}}") + "}"


def sql_login_connection_string(credentials: SynapseCredentials, host: str) -> str:
    return ";".join(
        [
            f"Server={host}",
            f"Database={credentials.database}",
            f"UID={braced(credentials.UID)}",
            f"PWD={braced(credentials.PWD)}",
            bool_to_connection_string_arg("Encrypt", bool(credentials.encrypt)),
            bool_to_connection_string_arg("TrustServerCertificate", bool(credentials.trust_cert)),
            f"ConnectRetryCount={credentials.retries}",
            "ConnectRetryInterval=10",
        ]
    )


class SynapseConnectionManager(FabricConnectionManager):
    TYPE = "synapse"

    @classmethod
    def open(cls, connection: Connection) -> Connection:
        if connection.state == ConnectionState.OPEN:
            logger.debug("Connection is already open, skipping open.")
            return connection

        # mssql-python 1.17 resets the isolation level when a pooled connection is closed,
        # and dedicated SQL pools reject it ("Setting IsolationLevel to ReadCommitted is not
        # supported"). The pool is process-wide, so it can only be turned off globally.
        mssql_python.pooling(enabled=False)

        if str(connection.credentials.authentication).lower() == "sql":
            return cls._open_with_sql_login(connection)
        return super().open(connection)

    @classmethod
    def _open_with_sql_login(cls, connection: Connection) -> Connection:
        credentials: SynapseCredentials = connection.credentials
        connection_string = sql_login_connection_string(credentials, cls.get_host(credentials))

        def connect():
            handle = mssql_python.connect(
                connection_string, autocommit=True, timeout=credentials.login_timeout
            )
            handle.timeout = credentials.query_timeout
            handle.add_output_converter(DATETIMEOFFSET_SQL_TYPE, byte_array_to_datetime)
            return handle

        return cls.retry_connection(
            connection,
            connect=connect,
            logger=logger,
            retry_limit=credentials.retries,
            retryable_exceptions=[mssql_python.InternalError, mssql_python.OperationalError],
        )

    # Dedicated SQL pools don't support DDL inside a user-defined transaction.
    def add_begin_query(self):
        pass

    def add_commit_query(self):
        pass

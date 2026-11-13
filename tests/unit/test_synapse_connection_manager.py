import mssql_python
import pytest
from dbt.adapters.contracts.connection import Connection, ConnectionState
from dbt.adapters.fabric import FabricConnectionManager
from mssql_python.connection_string_parser import _ConnectionStringParser

from dbt.adapters.synapse.synapse_connection_manager import (
    SynapseConnectionManager,
    sql_login_connection_string,
)
from dbt.adapters.synapse.synapse_credentials import SynapseCredentials


def make_credentials(**overrides):
    values = {
        "host": "myworkspace.sql.azuresynapse.net",
        "database": "mypool",
        "schema": "dbo",
        "authentication": "sql",
        "UID": "dbt_user",
        "PWD": "p;ss}word",
        **overrides,
    }
    return SynapseCredentials(**values)


def make_connection(credentials):
    return Connection(
        type="synapse", name="test", state=ConnectionState.INIT, credentials=credentials
    )


class FakeHandle:
    def __init__(self):
        self.timeout = None
        self.converters = {}

    def add_output_converter(self, sql_type, func):
        self.converters[sql_type] = func


@pytest.fixture
def driver_calls(monkeypatch):
    calls = {"connect": [], "pooling": []}

    def fake_connect(connection_string, **kwargs):
        calls["connect"].append((connection_string, kwargs))
        return FakeHandle()

    monkeypatch.setattr(mssql_python, "connect", fake_connect)
    monkeypatch.setattr(mssql_python, "pooling", lambda **kwargs: calls["pooling"].append(kwargs))
    return calls


def test_sql_login_connection_string_escapes_credentials():
    connection_string = sql_login_connection_string(make_credentials(), "host.example.net")

    parsed = _ConnectionStringParser()._parse(connection_string)

    assert parsed["server"] == "host.example.net"
    assert parsed["database"] == "mypool"
    assert parsed["uid"] == "dbt_user"
    assert parsed["pwd"] == "p;ss}word"
    assert "Encrypt=Yes" in connection_string
    assert "TrustServerCertificate=No" in connection_string


def test_open_with_sql_login_connects_with_password(driver_calls):
    connection = SynapseConnectionManager.open(make_connection(make_credentials()))

    assert connection.state == ConnectionState.OPEN
    [(connection_string, kwargs)] = driver_calls["connect"]
    assert "UID={dbt_user}" in connection_string
    assert kwargs["autocommit"] is True
    assert -155 in connection.handle.converters


@pytest.mark.parametrize("authentication", ["sql", "CLI"])
def test_open_disables_connection_pooling(driver_calls, monkeypatch, authentication):
    monkeypatch.setattr(FabricConnectionManager, "open", classmethod(lambda cls, conn: conn))

    SynapseConnectionManager.open(make_connection(make_credentials(authentication=authentication)))

    assert driver_calls["pooling"] == [{"enabled": False}]


def test_open_delegates_entra_authentication_to_fabric(driver_calls, monkeypatch):
    opened = []
    monkeypatch.setattr(
        FabricConnectionManager, "open", classmethod(lambda cls, conn: opened.append(conn) or conn)
    )
    connection = make_connection(make_credentials(authentication="CLI"))

    SynapseConnectionManager.open(connection)

    assert opened == [connection]
    assert driver_calls["connect"] == []


def test_open_skips_an_open_connection(driver_calls):
    connection = make_connection(make_credentials())
    connection.state = ConnectionState.OPEN

    assert SynapseConnectionManager.open(connection) is connection
    assert driver_calls == {"connect": [], "pooling": []}


@pytest.mark.parametrize("method", ["add_begin_query", "add_commit_query"])
def test_transaction_statements_are_not_sent(method):
    class Recorder:
        def add_query(self, sql, *args, **kwargs):
            raise AssertionError(f"unexpected query: {sql}")

    assert getattr(SynapseConnectionManager, method)(Recorder()) is None

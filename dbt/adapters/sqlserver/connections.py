from contextlib import contextmanager

import pyodbc
import os
import time
import struct

import dbt.exceptions
from dbt.adapters.sqlserver import SQLServerConnectionManager
from dbt.adapters.sqlserver import SQLServerCredentials
from azure.identity import DefaultAzureCredential

from dbt.logger import GLOBAL_LOGGER as logger

from dataclasses import dataclass
from typing import Optional


def create_token(tenant_id, client_id, client_secret):
    # bc DefaultAzureCredential will look in env variables
    os.environ["AZURE_TENANT_ID"] = tenant_id
    os.environ["AZURE_CLIENT_ID"] = client_id
    os.environ["AZURE_CLIENT_SECRET"] = client_secret

    token = DefaultAzureCredential().get_token("https://database.windows.net//.default")
    # convert to byte string interspersed with the 1-byte
    # TODO decide which is cleaner?
    # exptoken=b''.join([bytes({i})+bytes(1) for i in bytes(token.token, "UTF-8")])
    exptoken = bytes(1).join([bytes(i, "UTF-8") for i in token.token]) + bytes(1)
    # make c object with bytestring length prefix
    tokenstruct = struct.pack("=i", len(exptoken)) + exptoken

    return tokenstruct


@dataclass
class SynapseCredentials(SQLServerCredentials):
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
        return "synapse"

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
            "trust_cert"
        )


class SynapseConnectionManager(SynapseConnectionManager):
    TYPE = "synapse"

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


                

            con_str_concat = ';'.join(con_str)
            
            index = []
            for i, elem in enumerate(con_str):
                if 'pwd=' in elem.lower():
                    index.append(i)
                    
            if len(index) !=0 :
                con_str[index[0]]="PWD=***"

            con_str_display = ';'.join(con_str)
            
            logger.debug(f'Using connection string: {con_str_display}')

            if type_auth != "ServicePrincipal":
                handle = pyodbc.connect(con_str_concat, autocommit=True)

            elif type_auth == "ServicePrincipal":

                # create token if it does not exist
                if cls.TOKEN is None:
                    tenant_id = getattr(credentials, "tenant_id", None)
                    client_id = getattr(credentials, "client_id", None)
                    client_secret = getattr(credentials, "client_secret", None)

                    cls.TOKEN = create_token(tenant_id, client_id, client_secret)

                handle = pyodbc.connect(
                    con_str_concat, attrs_before={1256: cls.TOKEN}, autocommit=True
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

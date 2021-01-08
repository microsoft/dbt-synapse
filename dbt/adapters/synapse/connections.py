from contextlib import contextmanager

import pyodbc
import os
import time
import struct

import dbt.exceptions
import dbt.adapters.sqlserver.connections as sqlserverconn
from dbt.adapters.sqlserver import SQLServerConnectionManager
from dbt.adapters.sqlserver import SQLServerCredentials

from dbt.logger import GLOBAL_LOGGER as logger

from dataclasses import dataclass
from typing import Optional


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


class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
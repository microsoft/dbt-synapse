
import time

from contextlib import contextmanager
import pyodbc

from dataclasses import dataclass

import dbt.exceptions
from dbt.adapters.sqlserver import (SQLServerConnectionManager,
                                    SQLServerCredentials)
from dbt.contracts.connection import AdapterResponse
from dbt.logger import GLOBAL_LOGGER as logger

@dataclass
class SynapseCredentials(SQLServerCredentials):

    @property
    def type(self):
        return "synapse"

class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
    TOKEN = None

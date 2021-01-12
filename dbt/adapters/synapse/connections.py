from contextlib import contextmanager

import pyodbc
import os
import time
import struct
from itertools import chain, repeat
from typing import Callable, Mapping

import dbt.exceptions
import dbt.adapters.sqlserver.connections as sqlserverconn
from dbt.adapters.sqlserver import SQLServerConnectionManager
from dbt.adapters.sqlserver import SQLServerCredentials
from azure.core.credentials import AccessToken
from azure.identity import AzureCliCredential, DefaultAzureCredential

from dbt.logger import GLOBAL_LOGGER as logger

from dataclasses import dataclass
from typing import Optional


AZURE_CREDENTIAL_SCOPE = "https://database.windows.net//.default"


@dataclass
class SynapseCredentials(SQLServerCredentials):

    @property
    def type(self):
        return "synapse"

class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
    TOKEN = None


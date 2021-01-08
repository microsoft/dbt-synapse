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


class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
from dataclasses import dataclass
from dbt.adapters.sqlserver import (SQLServerConnectionManager,
                                    SQLServerCredentials)

@dataclass
class SynapseCredentials(SQLServerCredentials):

    @property
    def type(self):
        return "synapse"

class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
    TOKEN = None

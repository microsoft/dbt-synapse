from dataclasses import dataclass

from dbt.adapters.sqlserver import SQLServerCredentials


@dataclass
class SynapseCredentials(SQLServerCredentials):
    @property
    def type(self):
        return "synapse"

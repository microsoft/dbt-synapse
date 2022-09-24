from dbt.adapters.sqlserver import SQLServerConnectionManager


class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
    TOKEN = None

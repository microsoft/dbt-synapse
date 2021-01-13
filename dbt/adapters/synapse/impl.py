from dbt.adapters.sqlserver import SQLServerAdapter
from dbt.adapters.synapse import SynapseConnectionManager



class SynapseAdapter(SQLServerAdapter):
    ConnectionManager = SynapseConnectionManager
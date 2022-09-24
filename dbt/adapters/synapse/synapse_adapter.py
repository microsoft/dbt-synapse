from dbt.adapters.sqlserver import SQLServerAdapter

from dbt.adapters.synapse.synapse_connection_manager import SynapseConnectionManager


class SynapseAdapter(SQLServerAdapter):
    ConnectionManager = SynapseConnectionManager

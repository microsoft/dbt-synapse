from dbt.adapters.fabric import FabricAdapter

from dbt.adapters.synapse.synapse_connection_manager import SynapseConnectionManager


class SynapseAdapter(FabricAdapter):
    ConnectionManager = SynapseConnectionManager

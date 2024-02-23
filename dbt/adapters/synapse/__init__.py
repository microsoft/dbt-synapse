from dbt.adapters.base import AdapterPlugin
from dbt.adapters.include import synapse

from dbt.adapters.synapse.synapse_adapter import SynapseAdapter
from dbt.adapters.synapse.synapse_column import SynapseColumn
from dbt.adapters.synapse.synapse_connection_manager import SynapseConnectionManager
from dbt.adapters.synapse.synapse_credentials import SynapseCredentials

Plugin = AdapterPlugin(
    adapter=SynapseAdapter,
    credentials=SynapseCredentials,
    include_path=synapse.PACKAGE_PATH,
    dependencies=["fabric"],
)

__all__ = [
    "Plugin",
    "SynapseConnectionManager",
    "SynapseColumn",
    "SynapseAdapter",
    "SynapseCredentials",
]

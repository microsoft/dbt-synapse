from dbt.adapters.base import AdapterPlugin

from dbt.adapters.synapse.synapse_adapter import SynapseAdapter
from dbt.adapters.synapse.synapse_connection_manager import SynapseConnectionManager
from dbt.adapters.synapse.synapse_credentials import SynapseCredentials
from dbt.include import synapse

Plugin = AdapterPlugin(
    adapter=SynapseAdapter,
    credentials=SynapseCredentials,
    include_path=synapse.PACKAGE_PATH,
    dependencies=["sqlserver"],
)

__all__ = ["Plugin", "SynapseConnectionManager", "SynapseAdapter", "SynapseCredentials"]

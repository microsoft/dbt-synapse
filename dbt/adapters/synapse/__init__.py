from dbt.adapters.base import AdapterPlugin

from dbt.adapters.synapse.connections import SynapseConnectionManager, SynapseCredentials
from dbt.adapters.synapse.impl import SynapseAdapter
from dbt.include import synapse

Plugin = AdapterPlugin(
    adapter=SynapseAdapter,
    credentials=SynapseCredentials,
    include_path=synapse.PACKAGE_PATH,
    dependencies=["sqlserver"],
)

__all__ = ["Plugin", "SynapseConnectionManager", "SynapseAdapter", "SynapseCredentials"]

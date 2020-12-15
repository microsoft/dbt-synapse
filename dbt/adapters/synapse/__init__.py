from dbt.adapters.synapse.connections import SynapseConnectionManager
from dbt.adapters.synapse.connections import SynapseCredentials
from dbt.adapters.synapse.impl import SynapseAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import synapse


Plugin = AdapterPlugin(
    adapter=SynapseAdapter,
    credentials=SynapseCredentials,
    include_path=synapse.PACKAGE_PATH,
    dependencies=['sqlserver']
)

from dbt.adapters.sqlserver import SQLServerAdapter
from dbt.adapters.synapse import SynapseConnectionManager
from dbt.adapters.synapse.relation import SynapseRelation



class SynapseAdapter(SQLServerAdapter):
    Relation = SynapseRelation
    ConnectionManager = SynapseConnectionManager
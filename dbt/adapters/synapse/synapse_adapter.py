from dbt.adapters.base.relation import BaseRelation
from dbt.adapters.cache import _make_ref_key_dict
from dbt.adapters.fabric import FabricAdapter
from dbt.adapters.sql.impl import CREATE_SCHEMA_MACRO_NAME
from dbt.events.functions import fire_event
from dbt.events.types import SchemaCreation

from dbt.adapters.synapse.synapse_connection_manager import SynapseConnectionManager


class SynapseAdapter(FabricAdapter):
    ConnectionManager = SynapseConnectionManager

    def create_schema(self, relation: BaseRelation) -> None:
        relation = relation.without_identifier()
        fire_event(SchemaCreation(relation=_make_ref_key_dict(relation)))
        macro_name = CREATE_SCHEMA_MACRO_NAME
        kwargs = {
            "relation": relation,
        }

        if self.config.credentials.schema_authorization:
            kwargs["schema_authorization"] = self.config.credentials.schema_authorization
            macro_name = "synapse__create_schema_with_authorization"

        self.execute_macro(macro_name, kwargs=kwargs)
        self.commit_if_has_connection()

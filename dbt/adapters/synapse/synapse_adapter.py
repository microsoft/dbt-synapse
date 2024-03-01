from enum import Enum
from typing import Any, Dict, List, Optional

from dbt.adapters.base.relation import BaseRelation
from dbt.adapters.cache import _make_ref_key_dict
from dbt.adapters.events.types import SchemaCreation
from dbt.adapters.fabric import FabricAdapter
from dbt.adapters.sql.impl import CREATE_SCHEMA_MACRO_NAME
from dbt_common.contracts.constraints import ColumnLevelConstraint, ConstraintType
from dbt_common.events.functions import fire_event

from dbt.adapters.synapse.synapse_column import SynapseColumn
from dbt.adapters.synapse.synapse_connection_manager import SynapseConnectionManager


class SynapseAdapter(FabricAdapter):
    ConnectionManager = SynapseConnectionManager
    Column = SynapseColumn

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

    class ConstraintSupport(str, Enum):
        ENFORCED = "enforced"
        NOT_ENFORCED = "not_enforced"
        NOT_SUPPORTED = "not_supported"

    # https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-table-constraints#table-constraints
    CONSTRAINT_SUPPORT = {
        ConstraintType.check: ConstraintSupport.NOT_SUPPORTED,  # no CHECK support for Synapse
        ConstraintType.not_null: ConstraintSupport.ENFORCED,
        ConstraintType.unique: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.primary_key: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.foreign_key: ConstraintSupport.NOT_SUPPORTED,  # no FK support for Synapse
    }

    @classmethod
    def render_column_constraint(cls, constraint: ColumnLevelConstraint) -> Optional[str]:
        """Render the given constraint as DDL text.
        Should be overriden by adapters which need custom constraint rendering."""
        if constraint.type == ConstraintType.check and constraint.expression:
            return f"check {constraint.expression}"
        elif constraint.type == ConstraintType.not_null:
            return "not null"
        elif constraint.type == ConstraintType.unique:
            return "unique NOT ENFORCED"
        elif constraint.type == ConstraintType.primary_key:
            return "primary key NONCLUSTERED NOT ENFORCED"
        elif constraint.type == ConstraintType.foreign_key:
            return "foreign key"
        elif constraint.type == ConstraintType.custom and constraint.expression:
            return constraint.expression
        else:
            return None

    @classmethod
    def render_raw_columns_constraints(cls, raw_columns: Dict[str, Dict[str, Any]]) -> List:
        rendered_column_constraints = []

        for v in raw_columns.values():
            rendered_column_constraint = [f"[{v['name']}] {v['data_type']}"]
            for con in v.get("constraints", None):
                constraint = cls._parse_column_constraint(con)
                c = cls.process_parsed_constraint(constraint, cls.render_column_constraint)
                if c is not None:
                    rendered_column_constraint.append(c)
            rendered_column_constraints.append(" ".join(rendered_column_constraint))

        return rendered_column_constraints

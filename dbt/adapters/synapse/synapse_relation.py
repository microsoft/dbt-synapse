from dataclasses import dataclass, field
from typing import Optional, Type

from dbt.adapters.base.relation import BaseRelation, Policy
from dbt.adapters.utils import classproperty

from dbt.adapters.synapse.relation_configs import SynapseIncludePolicy, SynapseQuotePolicy, SynapseRelationType


@dataclass(frozen=True, eq=False, repr=False)
class SynapseRelation(BaseRelation):
    type: Optional[SynapseRelationType] = None  # type: ignore
    quote_policy: SynapseQuotePolicy = field(default_factory=lambda: SynapseQuotePolicy())
    include_policy: Policy = field(default_factory=lambda: SynapseIncludePolicy())

    @classproperty
    def get_relation_type(cls) -> Type[SynapseRelationType]:
        return SynapseRelationType

    def render_limited(self) -> str:
        rendered = self.render()
        if self.limit is None:
            return rendered
        elif self.limit == 0:
            return f"(select top(0) * from {rendered} where false) _dbt_limit_subq"
        else:
            return f"(select top({self.limit}) * from {rendered}) _dbt_limit_subq"
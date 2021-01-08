from dbt.adapters.sqlserver import SQLServerAdapter
from dbt.adapters.synapse import SynapseConnectionManager
from dbt.adapters.base.relation import BaseRelation
from typing import (
    Optional, Tuple, Callable, Iterable, Type, Dict, Any, List, Mapping,
    Iterator, Union, Set
)


class SynapseAdapter(SQLServerAdapter):
    ConnectionManager = SynapseConnectionManager
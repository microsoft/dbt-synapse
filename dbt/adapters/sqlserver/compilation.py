from typing import List, Dict, Any, Tuple, cast, Optional

from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.compiled import (
    CompiledDataTestNode,
    NonSourceCompiledNode,
)

from dbt.compilation import Compiler

class TSQLCompiler(Compiler):

    def _get_dbt_test_name(self) -> str:
        # I understand that in T-SQL, '[#identifier]' means 'temporary'
        return '#dbt__CTE__INTERNAL_test'

    def _add_ctes(
        self,
        compiled_node: NonSourceCompiledNode,
        manifest: Manifest,
        extra_context: Dict[str, Any],
    ) -> NonSourceCompiledNode:
        """Wrap data tests in a warm-yet-temporary blanket."""

        # we need to wrap data test queries in such a way that we can 
        # `select count(*)` at the end.
        if isinstance(compiled_node, CompiledDataTestNode):
            # create a temp table with the data test query, then get its count
            name = self._get_dbt_test_name()
            compiled_node.compiled_sql = f'''
                create table {name} as \n{compiled_node.compiled_sql};\n
                select count(*) from {name}
            '''.strip()

        return compiled_node

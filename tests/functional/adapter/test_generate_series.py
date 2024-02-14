import pytest
from dbt.tests.adapter.utils.base_utils import BaseUtils
from dbt.tests.adapter.utils.fixture_generate_series import models__test_generate_series_yml

# Cause of overriding fixture: Specifying more than one WITH clause in a CTE isn't allowed.
# For example, if a CTE query definition contains a subquery,
# that subquery can't contain a nested WITH clause that defines another CTE.

models__test_generate_series_sql = """
    {{ dbt.generate_series(10) }}
    left join (
        select 1 as expected
        union all
        select 2 as expected
        union all
        select 3 as expected
        union all
        select 4 as expected
        union all
        select 5 as expected
        union all
        select 6 as expected
        union all
        select 7 as expected
        union all
        select 8 as expected
        union all
        select 9 as expected
        union all
        select 10 as expected
    ) as expected_numbers
    on generate_series.generated_number = expected_numbers.expected
"""


class BaseGenerateSeries(BaseUtils):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_generate_series.yml": models__test_generate_series_yml,
            "test_generate_series.sql": self.interpolate_macro_namespace(
                models__test_generate_series_sql, "generate_series"
            ),
        }


class TestGenerateSeries(BaseGenerateSeries):
    pass

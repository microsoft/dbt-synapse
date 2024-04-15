import pytest
from dbt.tests.adapter.dbt_show.test_dbt_show import (
    models__sample_model,
    models__sql_header,
    seeds__sample_seed,
)
from dbt.tests.util import run_dbt

models__sample_model_a = """
select
    coalesce(sample_num, 0) + 10 as col_deci
from {{ ref('sample_model') }}
"""

models__sample_model_b = """
select
    col_deci + 100 as col_hundo
from {{ ref('sample_model_a') }}
"""


# Synapse doesn't support ephemeral models so we need to alter the base tests
class BaseShowLimit:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sample_model.sql": models__sample_model,
            "sample_model_a.sql": models__sample_model_a,
        }

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"sample_seed.csv": seeds__sample_seed}

    @pytest.mark.parametrize(
        "args,expected",
        [
            ([], 5),  # default limit
            (["--limit", 3], 3),  # fetch 3 rows
            (["--limit", -1], 7),  # fetch all rows
        ],
    )
    def test_limit(self, project, args, expected):
        run_dbt(["build"])
        dbt_args = ["show", "--inline", models__sample_model_b, *args]
        results = run_dbt(dbt_args)
        assert len(results.results[0].agate_table) == expected
        # ensure limit was injected in compiled_code when limit specified in command args
        limit = results.args.get("limit")
        if limit > 0:
            assert f"top {limit}" in results.results[0].node.compiled_code


class BaseShowSqlHeader:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sql_header.sql": models__sql_header,
        }

    def test_sql_header(self, project):
        run_dbt(["show", "--select", "sql_header", "--vars", "timezone: Asia/Kolkata"])


class TestShowSqlHeaderSynapse(BaseShowSqlHeader):
    pass


# Disabled because dbt-synapse doesn't support the `--limit` flag
# class TestShowLimitSynapse(BaseShowLimit):
#     pass
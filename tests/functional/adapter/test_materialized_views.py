import pytest
from dbt.tests.adapter.materialized_view.basic import MaterializedViewBasic
from dbt.tests.util import (
    assert_message_in_logs,
    check_relation_types,
    get_model_file,
    run_dbt,
    run_dbt_and_capture,
    set_model_file,
)

MY_TABLE = """
{{ config(
    materialized='table',
) }}
select i.id, count(i.value) as counted
from {{ ref('my_seed') }} i
group by i.id
"""


MY_VIEW = """
{{ config(
    materialized='view',
) }}
select i.id, count(i.value) as counted
from {{ ref('my_seed') }} i
group by i.id
"""


MY_MATERIALIZED_VIEW = """
{{ config(
    materialized='materialized_view',
) }}
select i.id, count(*) as counted
from {{ ref('my_seed') }} i
group by i.id
"""


class TestMaterializedViewsBasicSynapse(MaterializedViewBasic):
    @pytest.fixture(scope="class", autouse=True)
    def models(self):
        yield {
            "my_table.sql": MY_TABLE,
            "my_view.sql": MY_VIEW,
            "my_materialized_view.sql": MY_MATERIALIZED_VIEW,
        }

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, project, my_materialized_view):
        run_dbt(["seed"])
        run_dbt(["run", "--models", my_materialized_view.identifier, "--full-refresh"])

        # the tests touch these files, store their contents in memory
        initial_model = get_model_file(project, my_materialized_view)

        yield

        # and then reset them after the test runs
        set_model_file(project, my_materialized_view, initial_model)

    def test_materialized_view_create(self, project):
        # check relation types
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_materialized_view": "view",
        }
        return check_relation_types(project.adapter, expected)

    def test_materialized_view_create_idempotent(self, project, my_materialized_view):
        # setup creates it once; verify it's there and run once
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_materialized_view": "view",
        }
        check_relation_types(project.adapter, expected)

        run_dbt(["run", "--models", my_materialized_view.identifier])
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_materialized_view": "view",
        }
        check_relation_types(project.adapter, expected)

    def test_materialized_view_full_refresh(self, project, my_materialized_view):
        _, logs = run_dbt_and_capture(
            ["--debug", "run", "--models", my_materialized_view.identifier, "--full-refresh"]
        )
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_materialized_view": "view",
        }
        check_relation_types(project.adapter, expected)
        assert_message_in_logs(f"Applying REPLACE to: {my_materialized_view}", logs)

    def test_materialized_view_replaces_table(self, project, my_table):
        run_dbt(["run", "--models", my_table.identifier])
        expected = {
            "my_table": "table",
        }
        check_relation_types(project.adapter, expected)

        self.swap_table_to_materialized_view(project, my_table)

        run_dbt(["run", "--models", my_table.identifier])
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_table": "view",
        }
        check_relation_types(project.adapter, expected)

    def test_materialized_view_replaces_view(self, project, my_view):
        run_dbt(["run", "--models", my_view.identifier])
        expected = {
            "my_view": "view",
        }
        check_relation_types(project.adapter, expected)

        self.swap_view_to_materialized_view(project, my_view)

        run_dbt(["run", "--models", my_view.identifier])
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_view": "view",
        }
        check_relation_types(project.adapter, expected)

    def test_table_replaces_materialized_view(self, project, my_materialized_view):
        run_dbt(["run", "--models", my_materialized_view.identifier])
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_materialized_view": "view",
        }
        check_relation_types(project.adapter, expected)

        self.swap_materialized_view_to_table(project, my_materialized_view)

        run_dbt(["run", "--models", my_materialized_view.identifier])
        expected = {
            "my_materialized_view": "table",
        }
        check_relation_types(project.adapter, expected)

    def test_view_replaces_materialized_view(self, project, my_materialized_view):
        run_dbt(["run", "--models", my_materialized_view.identifier])
        expected = {
            # sys.objects has no type "materialized view", it's type "view"
            "my_materialized_view": "view",
        }
        check_relation_types(project.adapter, expected)

        self.swap_materialized_view_to_view(project, my_materialized_view)

        run_dbt(["run", "--models", my_materialized_view.identifier])
        expected = {
            "my_materialized_view": "view",
        }
        check_relation_types(project.adapter, expected)

    @pytest.mark.skip(reason="Synapse materialized view is always updated")
    def test_materialized_view_only_updates_after_refresh(
        self, project, my_materialized_view, my_seed
    ):
        pass

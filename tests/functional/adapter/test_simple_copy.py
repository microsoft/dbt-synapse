from pathlib import Path

import pytest
from dbt.tests.adapter.simple_copy.fixtures import _SEEDS__SEED_UPDATE
from dbt.tests.adapter.simple_copy.test_simple_copy import SimpleCopySetup
from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import check_relations_equal, rm_file, run_dbt, write_file


class SynapseTestProjInfo(TestProjInfo):
    # This return a dictionary of table names to 'view' or 'table' values.
    # Override class because Synapse doesnt have 'ILIKE'
    def synapse_get_tables_in_schema(self):
        sql = """
                select table_name,
                        case when table_type = 'BASE TABLE' then 'table'
                            when table_type = 'VIEW' then 'view'
                            else table_type
                        end as materialization
                from information_schema.tables
                where {}
                order by table_name
                """
        sql = sql.format("{} like '{}'".format("table_schema", self.test_schema))
        result = self.run_sql(sql, fetch="all")
        return {model_name: materialization for (model_name, materialization) in result}


# create new project fixture replacing the syntax-incompatible method
@pytest.fixture
def synapse_project(project):
    # Replace the original class with the new one
    project.__class__ = SynapseTestProjInfo

    return project


class SimpleCopyBase(SimpleCopySetup):
    def test_simple_copy(self, synapse_project):
        # Load the seed file and check that it worked
        results = run_dbt(["seed"])
        assert len(results) == 1

        # Run the synapse_project and ensure that all the models loaded
        results = run_dbt()
        assert len(results) == 7
        check_relations_equal(
            synapse_project.adapter,
            ["seed", "view_model", "incremental", "materialized", "get_and_ref"],
        )

        # Change the seed.csv file and see if everything is the same,
        # i.e. everything has been updated
        main_seed_file = synapse_project.project_root / Path("seeds") / Path("seed.csv")
        rm_file(main_seed_file)
        write_file(_SEEDS__SEED_UPDATE, main_seed_file)
        results = run_dbt(["seed"])
        assert len(results) == 1
        results = run_dbt()
        assert len(results) == 7
        check_relations_equal(
            synapse_project.adapter,
            ["seed", "view_model", "incremental", "materialized", "get_and_ref"],
        )

    @pytest.mark.skip(reason="We are not supporting materialized views yet")
    def test_simple_copy_with_materialized_views(self, synapse_project):
        synapse_project.run_sql(
            f"create table {synapse_project.test_schema}.unrelated_table (id int)"
        )
        sql = f"""
            create materialized view {synapse_project.test_schema}.unrelated_materialized_view as (
                select * from {synapse_project.test_schema}.unrelated_table
            )
        """
        synapse_project.run_sql(sql)
        sql = f"""
            create view {synapse_project.test_schema}.unrelated_view as (
                select * from {synapse_project.test_schema}.unrelated_materialized_view
            )
        """
        synapse_project.run_sql(sql)
        results = run_dbt(["seed"])
        assert len(results) == 1
        results = run_dbt()
        assert len(results) == 7


class EmptyModelsArentRunBaseSynapse(SimpleCopySetup):
    def test_dbt_doesnt_run_empty(self, synapse_project):
        results = run_dbt(["seed"])
        assert len(results) == 1
        results = run_dbt()
        assert len(results) == 7

        # Overwriting the original method with the custom implementation
        tables = synapse_project.synapse_get_tables_in_schema()

        assert "empty" not in tables.keys()
        assert "disabled" not in tables.keys()


class TestSimpleCopyBaseSynapse(SimpleCopyBase):
    pass


class TestEmptyModelsArentRunSynapse(EmptyModelsArentRunBaseSynapse):
    pass

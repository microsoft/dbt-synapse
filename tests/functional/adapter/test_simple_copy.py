from pathlib import Path

import pytest
from dbt.adapters.factory import get_adapter_by_type
from dbt.tests.adapter.simple_copy.fixtures import _SEEDS__SEED_UPDATE
from dbt.tests.adapter.simple_copy.test_simple_copy import SimpleCopySetup
from dbt.tests.util import (
    check_relations_equal,
    get_connection,
    rm_file,
    run_dbt,
    run_sql_with_adapter,
    write_file,
)


class TestProjInfoSynapse:
    __test__ = False

    def __init__(
        self,
        project_root,
        profiles_dir,
        adapter_type,
        test_dir,
        shared_data_dir,
        test_data_dir,
        test_schema,
        database,
        test_config,
    ):
        self.project_root = project_root
        self.profiles_dir = profiles_dir
        self.adapter_type = adapter_type
        self.test_dir = test_dir
        self.shared_data_dir = shared_data_dir
        self.test_data_dir = test_data_dir
        self.test_schema = test_schema
        self.database = database
        self.test_config = test_config
        self.created_schemas = []

    @property
    def adapter(self):
        # This returns the last created "adapter" from the adapter factory. Each
        # dbt command will create a new one. This allows us to avoid patching the
        # providers 'get_adapter' function.
        return get_adapter_by_type(self.adapter_type)

    # Run sql from a path
    def run_sql_file(self, sql_path, fetch=None):
        with open(sql_path, "r") as f:
            statements = f.read().split(";")
            for statement in statements:
                self.run_sql(statement, fetch)

    # Run sql from a string, using adapter saved at test startup
    def run_sql(self, sql, fetch=None):
        return run_sql_with_adapter(self.adapter, sql, fetch=fetch)

    # Create the unique test schema. Used in test setup, so that we're
    # ready for initial sql prior to a run_dbt command.
    def create_test_schema(self, schema_name=None):
        if schema_name is None:
            schema_name = self.test_schema
        with get_connection(self.adapter):
            relation = self.adapter.Relation.create(database=self.database, schema=schema_name)
            self.adapter.create_schema(relation)
            self.created_schemas.append(schema_name)

    # Drop the unique test schema, usually called in test cleanup
    def drop_test_schema(self):
        with get_connection(self.adapter):
            for schema_name in self.created_schemas:
                relation = self.adapter.Relation.create(database=self.database, schema=schema_name)
                self.adapter.drop_schema(relation)
            self.created_schemas = []

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
    project.__class__ = TestProjInfoSynapse

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

    # in Synapse materialized views must be created with aggregation and distribution option
    def test_simple_copy_with_materialized_views(self, synapse_project):
        synapse_project.run_sql(
            f"create table {synapse_project.test_schema}.unrelated_table (id int)"
        )
        sql = f"""
            create materialized view {synapse_project.test_schema}.unrelated_materialized_view
            with ( distribution = round_robin ) as (
                select id from {synapse_project.test_schema}.unrelated_table group by id
            )
        """
        synapse_project.run_sql(sql)
        sql = f"""
            create view {synapse_project.test_schema}.unrelated_view as (
                select id from {synapse_project.test_schema}.unrelated_materialized_view
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

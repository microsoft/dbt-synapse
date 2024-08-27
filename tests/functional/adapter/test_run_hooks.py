import os
from pathlib import Path

import pytest
from dbt.tests.adapter.hooks.test_run_hooks import TestAfterRunHooks, TestPrePostRunHooks


class TestPrePostRunHooks(TestPrePostRunHooks):
    @pytest.fixture(scope="function")
    def setUp(self, project):
        project.run_sql_file(project.test_data_dir / Path("seed_run.sql"))
        project.run_sql(
            f"""
            if object_id ('{ project.test_schema }.schemas') is not null
            drop table { project.test_schema }.schemas
            """
        )
        project.run_sql(
            f"""
            if object_id ('{ project.test_schema }.db_schemas') is not null
            drop table { project.test_schema }.db_schemas
            """
        )
        os.environ["TERM_TEST"] = "TESTING"

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            # The create and drop table statements here validate that these hooks run
            # in the same order that they are defined. Drop before create is an error.
            # Also check that the table does not exist below.
            "on-run-start": [
                "{{ custom_run_hook('start', target, run_started_at, invocation_id) }}",
                "create table {{ target.schema }}.start_hook_order_test ( id int )",
                "drop table {{ target.schema }}.start_hook_order_test",
                "{{ log(env_var('TERM_TEST'), info=True) }}",
            ],
            "on-run-end": [
                "{{ custom_run_hook('end', target, run_started_at, invocation_id) }}",
                "create table {{ target.schema }}.end_hook_order_test ( id int )",
                "drop table {{ target.schema }}.end_hook_order_test",
                "create table {{ target.schema }}.schemas ( sch varchar(100) )",
                """insert into {{ target.schema }}.schemas (sch) values
                {% for schema in schemas %}( '{{ schema }}' )
                {% if not loop.last %},{% endif %}{% endfor %}""",
                """create table {{ target.schema }}.db_schemas
                ( db varchar(100), sch varchar(100) )""",
                """insert into {{ target.schema }}.db_schemas (db, sch) values
                {% for db, schema in database_schemas %}('{{ db }}', '{{ schema }}' )
                {% if not loop.last %},{% endif %}{% endfor %}""",
            ],
            "seeds": {
                "quote_columns": False,
            },
        }

    def check_hooks(self, state, project, host):
        ctx = self.get_ctx_vars(state, project)

        assert ctx["test_state"] == state
        assert ctx["target_dbname"] == ""
        assert ctx["target_host"] == ""
        assert ctx["target_name"] == "default"
        assert ctx["target_schema"] == project.test_schema
        assert ctx["target_threads"] == 1
        assert ctx["target_type"] == "synapse"
        # assert ctx["target_user"] == "None"
        assert ctx["target_pass"] == ""

        assert (
            ctx["run_started_at"] is not None and len(ctx["run_started_at"]) > 0
        ), "run_started_at was not set"
        assert (
            ctx["invocation_id"] is not None and len(ctx["invocation_id"]) > 0
        ), "invocation_id was not set"
        assert ctx["thread_id"].startswith("Thread-") or ctx["thread_id"] == "MainThread"


class TestAfterRunHooks(TestAfterRunHooks):
    pass

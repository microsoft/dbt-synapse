import pytest
from dbt.tests.adapter.hooks.fixtures import (
    models__hooks,
    models__hooks_configured,
    models__hooks_kwargs,
)
from dbt.tests.adapter.hooks.test_model_hooks import (
    MODEL_POST_HOOK,
    MODEL_PRE_HOOK,
    BaseTestPrePost,
    TestDuplicateHooksInConfigs,
    TestHooksRefsOnSeeds,
    TestPrePostModelHooksOnSeeds,
    TestPrePostModelHooksOnSeedsPlusPrefixed,
    TestPrePostModelHooksOnSeedsPlusPrefixedWhitespace,
    TestPrePostModelHooksOnSnapshots,
    TestPrePostSnapshotHooksInConfigKwargs,
)
from dbt.tests.util import run_dbt


class BaseTestPrePostSynapse(BaseTestPrePost):
    def check_hooks(self, state, project, host, count=1):
        ctxs = self.get_ctx_vars(state, count=count, project=project)
        for ctx in ctxs:
            assert ctx["test_state"] == state
            assert ctx["target_dbname"] == ""
            assert ctx["target_host"] == ""
            assert ctx["target_name"] == "default"
            assert ctx["target_schema"] == project.test_schema
            assert ctx["target_threads"] == 1
            assert ctx["target_type"] == "synapse"
            # assert ctx["target_user"] == "dbttestuser"
            assert ctx["target_pass"] == ""

            assert (
                ctx["run_started_at"] is not None and len(ctx["run_started_at"]) > 0
            ), "run_started_at was not set"
            assert (
                ctx["invocation_id"] is not None and len(ctx["invocation_id"]) > 0
            ), "invocation_id was not set"
            assert ctx["thread_id"].startswith("Thread-")


class PrePostModelHooksInConfigSetup(BaseTestPrePostSynapse):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "macro-paths": ["macros"],
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {"hooks.sql": models__hooks_configured}


class TestHookRefs(BaseTestPrePostSynapse):
    pass


class TestPrePostModelHooksOnSeeds(TestPrePostModelHooksOnSeeds):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "seed-paths": ["seeds"],
            "models": {},
            "seeds": {
                "post-hook": [
                    "alter table {{ this }} add new_col int",
                    "update {{ this }} set new_col = 1",
                    # call any macro to track dependency:
                    # https://github.com/dbt-labs/dbt-core/issues/6806
                    "select cast(null as {{ dbt.type_int() }}) as id",
                ],
                "quote_columns": False,
            },
        }


class TestHooksRefsOnSeeds(TestHooksRefsOnSeeds):
    pass


#
class TestPrePostModelHooksOnSeedsPlusPrefixed(TestPrePostModelHooksOnSeedsPlusPrefixed):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "seed-paths": ["seeds"],
            "models": {},
            "seeds": {
                "+post-hook": [
                    "alter table {{ this }} add new_col int",
                    "update {{ this }} set new_col = 1",
                ],
                "quote_columns": False,
            },
        }


class TestPrePostModelHooksOnSeedsPlusPrefixedWhitespace(
    TestPrePostModelHooksOnSeedsPlusPrefixedWhitespace
):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "seed-paths": ["seeds"],
            "models": {},
            "seeds": {
                "+post-hook": [
                    "alter table {{ this }} add new_col int",
                    "update {{ this }} set new_col = 1",
                ],
                "quote_columns": False,
            },
        }


class TestPrePostModelHooksOnSnapshots(TestPrePostModelHooksOnSnapshots):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "seed-paths": ["seeds"],
            "snapshot-paths": ["test-snapshots"],
            "models": {},
            "snapshots": {
                "post-hook": [
                    "alter table {{ this }} add new_col int",
                    "update {{ this }} set new_col = 1",
                ]
            },
            "seeds": {
                "quote_columns": False,
            },
        }


class TestPrePostModelHooksInConfig(PrePostModelHooksInConfigSetup):
    def test_pre_and_post_model_hooks_model(self, project, dbt_profile_target):
        run_dbt()

        self.check_hooks("start", project, dbt_profile_target.get("host", None))
        self.check_hooks("end", project, dbt_profile_target.get("host", None))


class TestPrePostModelHooksInConfigKwargs(TestPrePostModelHooksInConfig):
    @pytest.fixture(scope="class")
    def models(self):
        return {"hooks.sql": models__hooks_kwargs}


class TestPrePostSnapshotHooksInConfigKwargs(TestPrePostSnapshotHooksInConfigKwargs):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "seed-paths": ["seeds"],
            "snapshot-paths": ["test-kwargs-snapshots"],
            "models": {},
            "snapshots": {
                "post-hook": [
                    "alter table {{ this }} add new_col int",
                    "update {{ this }} set new_col = 1",
                ]
            },
            "seeds": {
                "quote_columns": False,
            },
        }


class TestDuplicateHooksInConfigs(TestDuplicateHooksInConfigs):
    pass


# vacuum command is removed because not supported in synapse
class TestPrePostModelHooks(BaseTestPrePostSynapse):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "models": {
                "test": {
                    "pre-hook": [MODEL_PRE_HOOK],
                    "post-hook": [MODEL_POST_HOOK],
                }
            }
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {"hooks.sql": models__hooks}

    def test_pre_and_post_run_hooks(self, project, dbt_profile_target):
        run_dbt()
        self.check_hooks("start", project, dbt_profile_target.get("host", None))
        self.check_hooks("end", project, dbt_profile_target.get("host", None))


class TestPrePostModelHooksInConfigWithCount(PrePostModelHooksInConfigSetup):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "models": {
                "test": {
                    "pre-hook": [MODEL_PRE_HOOK],
                    "post-hook": [MODEL_POST_HOOK],
                }
            }
        }

    def test_pre_and_post_model_hooks_model_and_project(self, project, dbt_profile_target):
        run_dbt()

        self.check_hooks("start", project, dbt_profile_target.get("host", None), count=2)
        self.check_hooks("end", project, dbt_profile_target.get("host", None), count=2)


@pytest.mark.skip(reason="Not supporting underscores config")
class TestPrePostModelHooksUnderscores(TestPrePostModelHooks):
    def project_config_update(self):
        return {
            "models": {
                "test": {
                    "pre_hook": [MODEL_PRE_HOOK],
                    "post_hook": [MODEL_POST_HOOK],
                }
            }
        }

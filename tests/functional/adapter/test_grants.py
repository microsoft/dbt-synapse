from dbt.tests.adapter.grants.test_incremental_grants import BaseIncrementalGrants
from dbt.tests.adapter.grants.test_invalid_grants import BaseInvalidGrants
from dbt.tests.adapter.grants.test_model_grants import BaseModelGrants
from dbt.tests.adapter.grants.test_seed_grants import BaseSeedGrants
from dbt.tests.adapter.grants.test_snapshot_grants import (
    BaseSnapshotGrants,
    user2_snapshot_schema_yml,
)
from dbt.tests.util import get_manifest, run_dbt, run_dbt_and_capture, write_file


class TestIncrementalGrantsSynapse(BaseIncrementalGrants):
    pass


class TestInvalidGrantsSynapse(BaseInvalidGrants):
    def grantee_does_not_exist_error(self):
        return "Cannot find the user"

    def privilege_does_not_exist_error(self):
        return "Incorrect syntax near"


class TestModelGrantsSynapse(BaseModelGrants):
    pass


class TestSeedGrantsSynapse(BaseSeedGrants):
    pass


class TestSnapshotGrantsSynapse(BaseSnapshotGrants):
    def test_snapshot_grants(self, project, get_test_users):
        test_users = get_test_users
        select_privilege_name = self.privilege_grantee_name_overrides()["select"]

        # run the snapshot
        results = run_dbt(["snapshot"])
        assert len(results) == 1
        manifest = get_manifest(project.project_root)
        snapshot_id = "snapshot.test.my_snapshot"
        snapshot = manifest.nodes[snapshot_id]
        expected = {select_privilege_name: [test_users[0]]}
        assert snapshot.config.grants == expected
        self.assert_expected_grants_match_actual(project, "my_snapshot", expected)

        # run it again, nothing should have changed
        # since dbt selects into temporary table, drops existing, selects into original table name,
        # SELECT needs to be granted again, so "grant " expected in log_output!
        (results, log_output) = run_dbt_and_capture(["--debug", "snapshot"])
        assert len(results) == 1
        assert "revoke " not in log_output
        assert "grant " in log_output  # grant expected
        self.assert_expected_grants_match_actual(project, "my_snapshot", expected)

        # change the grantee, assert it updates
        updated_yaml = self.interpolate_name_overrides(user2_snapshot_schema_yml)
        write_file(updated_yaml, project.project_root, "snapshots", "schema.yml")
        (results, log_output) = run_dbt_and_capture(["--debug", "snapshot"])
        assert len(results) == 1
        expected = {select_privilege_name: [test_users[1]]}
        self.assert_expected_grants_match_actual(project, "my_snapshot", expected)

import pytest
from dbt.tests.adapter.grants.test_incremental_grants import BaseIncrementalGrants
from dbt.tests.adapter.grants.test_invalid_grants import BaseInvalidGrants
from dbt.tests.adapter.grants.test_model_grants import BaseModelGrants
from dbt.tests.adapter.grants.test_seed_grants import BaseSeedGrants
from dbt.tests.adapter.grants.test_snapshot_grants import BaseSnapshotGrants


class TestIncrementalGrantsSynapse(BaseIncrementalGrants):
    pass


class TestInvalidGrantsSQLServer(BaseInvalidGrants):
    def grantee_does_not_exist_error(self):
        return "Cannot find the user"

    def privilege_does_not_exist_error(self):
        return "Incorrect syntax near"


class TestModelGrantsSynapse(BaseModelGrants):
    pass


class TestSeedGrantsSynapse(BaseSeedGrants):
    pass


class TestSnapshotGrantsSynapse(BaseSnapshotGrants):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            # ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
            # Merge statements with a WHEN NOT MATCHED [BY TARGET] clause must
            # target a hash distributed table. (100087) (SQLExecDirectW)')
            "snapshots": {"test": {"dist": "HASH(id)", "index": "HEAP"}},
        }

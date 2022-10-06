import pytest
from dbt.tests.adapter.grants.test_incremental_grants import BaseIncrementalGrants
from dbt.tests.adapter.grants.test_invalid_grants import BaseInvalidGrants
from dbt.tests.adapter.grants.test_model_grants import BaseModelGrants
from dbt.tests.adapter.grants.test_seed_grants import BaseSeedGrants
from dbt.tests.adapter.grants.test_snapshot_grants import BaseSnapshotGrants


class TestIncrementalGrantsSynapse(BaseIncrementalGrants):
    pass


@pytest.mark.skip(reason="Azure error messages inconsistent")
class TestInvalidGrantsSynapse(BaseInvalidGrants):
    # This test does not run on Azure since the error messages are inconsistent there.
    # Tests have shown errors like "principal x could not be found"
    # as well as "principal x could not be resolved"
    pass


class TestModelGrantsSynapse(BaseModelGrants):
    pass


class TestSeedGrantsSynapse(BaseSeedGrants):
    pass


class TestSnapshotGrantsSynapse(BaseSnapshotGrants):
    pass

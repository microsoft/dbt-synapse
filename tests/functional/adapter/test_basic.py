import pytest
from dbt.tests.adapter.basic.test_adapter_methods import BaseAdapterMethod
from dbt.tests.adapter.basic.test_base import BaseSimpleMaterializations
from dbt.tests.adapter.basic.test_empty import BaseEmpty
from dbt.tests.adapter.basic.test_ephemeral import BaseEphemeral
from dbt.tests.adapter.basic.test_generic_tests import BaseGenericTests
from dbt.tests.adapter.basic.test_incremental import BaseIncremental
from dbt.tests.adapter.basic.test_singular_tests import BaseSingularTests
from dbt.tests.adapter.basic.test_singular_tests_ephemeral import BaseSingularTestsEphemeral
from dbt.tests.adapter.basic.test_snapshot_check_cols import BaseSnapshotCheckCols
from dbt.tests.adapter.basic.test_snapshot_timestamp import BaseSnapshotTimestamp


class TestSimpleMaterializationsSynapse(BaseSimpleMaterializations):
    pass


class TestSingularTestsSynapse(BaseSingularTests):
    pass


@pytest.mark.skip(reason="ephemeral not supported")
class TestSingularTestsEphemeralSynapse(BaseSingularTestsEphemeral):
    pass


class TestEmptySynapse(BaseEmpty):
    pass


class TestEphemeralSynapse(BaseEphemeral):
    pass


class TestIncrementalSynapse(BaseIncremental):
    pass


class TestGenericTestsSynapse(BaseGenericTests):
    pass


class TestSnapshotCheckColsSynapse(BaseSnapshotCheckCols):
    pass


class TestSnapshotTimestampSynapse(BaseSnapshotTimestamp):
    pass


class TestBaseAdapterMethodSynapse(BaseAdapterMethod):
    pass

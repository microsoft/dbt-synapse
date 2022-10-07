import pytest
from dbt.tests.adapter.basic.test_adapter_methods import BaseAdapterMethod
from dbt.tests.adapter.basic.test_base import BaseSimpleMaterializations
from dbt.tests.adapter.basic.test_empty import BaseEmpty
from dbt.tests.adapter.basic.test_ephemeral import BaseEphemeral
from dbt.tests.adapter.basic.test_generic_tests import BaseGenericTests
from dbt.tests.adapter.basic.test_incremental import (
    BaseIncremental,
    BaseIncrementalNotSchemaChange,
)
from dbt.tests.adapter.basic.test_singular_tests import BaseSingularTests
from dbt.tests.adapter.basic.test_singular_tests_ephemeral import BaseSingularTestsEphemeral
from dbt.tests.adapter.basic.test_snapshot_check_cols import BaseSnapshotCheckCols
from dbt.tests.adapter.basic.test_snapshot_timestamp import BaseSnapshotTimestamp
from dbt.tests.adapter.basic.test_validate_connection import BaseValidateConnection


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


class TestIncrementalNotSchemaChangeSynapse(BaseIncrementalNotSchemaChange):
    @pytest.fixture(scope="class")
    def models(self):
        incremental_not_schema_change_sql = """
{{ config(
    materialized="incremental",
    unique_key="user_id_current_time",
    on_schema_change="sync_all_columns") }}
select
    1 + '-' + current_timestamp as user_id_current_time,
    {% if is_incremental() %}
        'thisis18characters' as platform
    {% else %}
        'okthisis20characters' as platform
    {% endif %}
            """
        return {"incremental_not_schema_change.sql": incremental_not_schema_change_sql}


class TestGenericTestsSynapse(BaseGenericTests):
    pass


class TestSnapshotCheckColsSynapse(BaseSnapshotCheckCols):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "snapshot_strategy_check_cols",
            "snapshots": {
                "snapshot_strategy_check_cols": {
                    "dist": "HASH(id)"
                }
            }
        }


class TestSnapshotTimestampSynapse(BaseSnapshotTimestamp):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "snapshot_strategy_timestamp",
            "snapshots": {
                "snapshot_strategy_timestamp": {
                    "dist": "HASH(id)"
                }
            }
        }


class TestBaseCachingSynapse(BaseAdapterMethod):
    pass


class TestValidateConnectionSynapse(BaseValidateConnection):
    pass

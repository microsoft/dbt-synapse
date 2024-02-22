from dbt.tests.adapter.store_test_failures_tests.basic import (
    StoreTestFailuresAsExceptions,
    StoreTestFailuresAsGeneric,
    StoreTestFailuresAsInteractions,
    StoreTestFailuresAsProjectLevelEphemeral,
    StoreTestFailuresAsProjectLevelOff,
    StoreTestFailuresAsProjectLevelView,
)


class TestStoreTestFailuresAsInteractionsBase(StoreTestFailuresAsInteractions):
    pass


class TestStoreTestFailuresAsProjectLevelOffBase(StoreTestFailuresAsProjectLevelOff):
    pass


class TestStoreTestFailuresAsProjectLevelViewBase(StoreTestFailuresAsProjectLevelView):
    pass


class TestStoreTestFailuresAsGenericBase(StoreTestFailuresAsGeneric):
    pass


class TestStoreTestFailuresAsProjectLevelEphemeralBase(StoreTestFailuresAsProjectLevelEphemeral):
    pass


class TestStoreTestFailuresAsExceptionsBase(StoreTestFailuresAsExceptions):
    pass

from dbt.tests.adapter.simple_seed.test_seed import (
    SeedUniqueDelimiterTestBase,
    TestSeedWithEmptyDelimiter,
    TestSeedWithWrongDelimiter,
)


class SeedUniqueDelimiterTestBaseSynapse(SeedUniqueDelimiterTestBase):
    pass


class TestSeedWithWrongDelimiterSynapse(TestSeedWithWrongDelimiter):
    pass


class TestSeedWithEmptyDelimiterSynapse(TestSeedWithEmptyDelimiter):
    pass

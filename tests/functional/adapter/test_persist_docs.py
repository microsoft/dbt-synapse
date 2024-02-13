import pytest
from dbt.tests.adapter.persist_docs.test_persist_docs import (
    BasePersistDocs,
    BasePersistDocsColumnMissing,
    BasePersistDocsCommentOnQuotedColumn,
)


@pytest.mark.skip(reason="Synapse does not support adding/updating extended properties")
class TestPersistDocsSynapse(BasePersistDocs):
    pass


@pytest.mark.skip(reason="Synapse does not support adding/updating extended properties")
class TestPersistDocsColumnMissingSynapse(BasePersistDocsColumnMissing):
    pass


@pytest.mark.skip(reason="Synapse does not support adding/updating extended properties")
class TestPersistDocsCommentOnQuotedColumnSynapse(BasePersistDocsCommentOnQuotedColumn):
    pass

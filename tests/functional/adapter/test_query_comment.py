from dbt.tests.adapter.query_comment.test_query_comment import (
    BaseEmptyQueryComments,
    BaseMacroArgsQueryComments,
    BaseMacroInvalidQueryComments,
    BaseMacroQueryComments,
    BaseNullQueryComments,
    BaseQueryComments,
)


class TestQueryCommentsSynapse(BaseQueryComments):
    pass


class TestMacroQueryCommentsSynapse(BaseMacroQueryComments):
    pass


class TestMacroArgsQueryCommentsSynapse(BaseMacroArgsQueryComments):
    pass


class TestMacroInvalidQueryCommentsSynapse(BaseMacroInvalidQueryComments):
    pass


class TestNullQueryCommentsSynapse(BaseNullQueryComments):
    pass


class TestEmptyQueryCommentsSynapse(BaseEmptyQueryComments):
    pass

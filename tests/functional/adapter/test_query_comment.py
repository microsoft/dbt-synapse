import json

from dbt.tests.adapter.query_comment.test_query_comment import (
    BaseEmptyQueryComments,
    BaseMacroArgsQueryComments,
    BaseMacroInvalidQueryComments,
    BaseMacroQueryComments,
    BaseNullQueryComments,
    BaseQueryComments,
)
from dbt.version import __version__ as dbt_version


class TestQueryCommentsSynapse(BaseQueryComments):
    pass


class TestMacroQueryCommentsSynapse(BaseMacroQueryComments):
    pass


class TestMacroArgsQueryCommentsSynapse(BaseMacroArgsQueryComments):
    def test_matches_comment(self, project):
        logs = self.run_get_json()
        expected_dct = {
            "app": "dbt++",
            "macro_version": "0.1.0",
            "message": f"blah: {project.adapter.config.target_name}",
        }
        expected = r"/* {} */\n".format(json.dumps(expected_dct, sort_keys=True)).replace(
            '"', r"\""
        )
        assert expected in logs


class TestMacroInvalidQueryCommentsSynapse(BaseMacroInvalidQueryComments):
    pass


class TestNullQueryCommentsSynapse(BaseNullQueryComments):
    pass


class TestEmptyQueryCommentsSynapse(BaseEmptyQueryComments):
    pass

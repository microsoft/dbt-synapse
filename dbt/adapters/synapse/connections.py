
from dataclasses import dataclass

from dbt.adapters.sqlserver import (SQLServerConnectionManager,
                                    SQLServerCredentials)
from dbt.contracts.connection import AdapterResponse

@dataclass
class SynapseCredentials(SQLServerCredentials):

    @property
    def type(self):
        return "synapse"

class SynapseConnectionManager(SQLServerConnectionManager):
    TYPE = "synapse"
    TOKEN = None

    @classmethod
    def get_response(cls, cursor) -> AdapterResponse:
        #message = str(cursor.statusmessage)
        message = 'OK'
        rows = cursor.rowcount
        #status_message_parts = message.split() if message is not None else []
        #status_messsage_strings = [
        #    part
        #    for part in status_message_parts
        #    if not part.isdigit()
        #]
        #code = ' '.join(status_messsage_strings)
        return AdapterResponse(
            _message=message,
            #code=code,
            rows_affected=rows
        )



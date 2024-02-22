from dataclasses import dataclass

from dbt.adapters.fabric import FabricCredentials


@dataclass
class SynapseCredentials(FabricCredentials):
    @property
    def type(self):
        return "synapse"

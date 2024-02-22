from dbt.adapters.fabric import FabricConnectionManager


class SynapseConnectionManager(FabricConnectionManager):
    TYPE = "synapse"
    TOKEN = None

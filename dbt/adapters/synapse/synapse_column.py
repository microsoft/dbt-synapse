from dbt.adapters.fabric import FabricColumn


class SynapseColumn(FabricColumn):
    # extending list of integer types for synapse
    def is_integer(self) -> bool:
        return self.dtype.lower() in [
            # real types
            "smallint",
            "bigint",
            "tinyint",
            "serial",
            "bigserial",
            "int",
            "bit",
        ]

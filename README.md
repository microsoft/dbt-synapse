# dbt-synapse

custom [dbt](https://www.getdbt.com) adapter for [Azure Synapse](https://azure.microsoft.com/en-us/services/synapse-analytics/). Major credit due to [@mikaelene](https://github.com/mikaelene) and [his `dbt-sqlserver` custom adapter](https://github.com/mikaelene/dbt-sqlserver).

## related packages
To get additional functionality, check out:
- [fishtown-analytics/dbt-external-tables](https://github.com/fishtown-analytics/dbt-external-tables) which allows for easy staging of blob sources defined in `YAML`, and
- [dbt-msft/tsql-utils](https://github.com/dbt-msft/tsql-utils) enables `dbt-synapse` to use [dbt-utils](https://github.com/fishtown-analytics/dbt-utils): the much-loved, extremely-useful collection of dbt macros.

## major differences b/w `dbt-synapse` and `dbt-sqlserver`
- macros use only Azure Synapse `T-SQL`. [Relevant GitHub issue](https://github.com/MicrosoftDocs/azure-docs/issues/55713)
- use of [Create Table as Select (CTAS)](https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?view=aps-pdw-2016-au7) means you don't need post-hooks to create indices (see Table Materializations section below for more info)
- rewrite of snapshots because Synapse doesn't support `MERGE`.

## status & support
as of now, only support for dbt `0.18.0`

Passing all tests in [dbt-adapter-tests](https://github.com/fishtown-analytics/dbt-adapter-tests), except `test_dbt_ephemeral_data_tests`

### outstanding work:
-  `ephemeral` materializations (workaround for non-recursive CTEs) see [#25](https://github.com/dbt-msft/dbt-synapse/issues/25)
- officially rename the adapter from `sqlserver` to `synapse` see [#40](https://github.com/swanderz/dbt-synapse/pull/6)
- Make seed creation more fault-tolerant [#36](https://github.com/dbt-msft/dbt-synapse/issues/36)

## Installation
Easiest install is to use pip (not yet registered on PyPI).

First install [ODBC Driver version 17](https://www.microsoft.com/en-us/download/details.aspx?id=56567).

```bash
pip install dbt-synapse
```

## Authentication

Please see the [Authentication section of dbt-sqlserver's README.md](https://github.com/dbt-msft/dbt-sqlserver#authentication)

## Table Materializations
CTAS allows you to materialize tables with indices and distributions at creation time, which obviates the need for post-hooks to set indices.

### Example
You can also configure `index` and `dist` in `dbt_project.yml`.
#### `models/stage/absence.sql
```
{{
    config(
        index='HEAP',
        dist='ROUND_ROBIN'
        )
}}

select *
from ...
```

is turned into the relative form (minus `__dbt`'s `_backup` and `_tmp` tables)

```SQL
  CREATE TABLE ajs_stg.absence_hours
    WITH(
      DISTRIBUTION = ROUND_ROBIN,
      HEAP
      )
    AS (SELECT * FROM ajs_stg.absence_hours__dbt_tmp_temp_view)
```
#### Indices
- `CLUSTERED COLUMNSTORE INDEX` (default)
- `HEAP`
- `CLUSTERED INDEX ({COLUMN})`
- `CLUSTERED COLUMNSTORE INDEX ORDER({{COLUMN}})` # see [docs](https://docs.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/performance-tuning-ordered-cci) for performance suggestions
  
#### Distributions
- `ROUND_ROBIN` (default)
- `HASH({COLUMN})`
- `REPLICATE`

# Changelog

See [CHANGELOG.md](CHANGELOG.md)
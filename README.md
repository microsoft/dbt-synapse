# dbt-synapse

custom [dbt](https://www.getdbt.com) adapter for [Azure Synapse](https://azure.microsoft.com/en-us/services/synapse-analytics/). Major credit due to @mikaelene and [his `sqlserver` custom adapter](https://github.com/mikaelene/dbt-sqlserver).

## major differences b/w `dbt-synapse` and `dbt-sqlserver`
- macros use only Azure Synapse `T-SQL`. [Relevant GitHub issue](https://github.com/MicrosoftDocs/azure-docs/issues/55713)
- use of [Create Table as Select (CTAS)](https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?view=aps-pdw-2016-au7) means you don't need post-hooks to create indices
- Azure Active Directory Authentication options
- rewrite of snapshots because Synapse doesn't support `MERGE`.
- external table creation via details from yaml.
  - must first create  `EXTERNAL DATA SOURCE` and `EXTERNAL FILE FORMAT`s.

## status & support
as of now, only support for dbt `0.18.0`

Passing all tests in [dbt-adapter-tests](https://github.com/fishtown-analytics/dbt-adapter-tests), except `test_dbt_ephemeral_data_tests`

### outstanding work:
-  `ephemeral` materializations (workaround for non-recursive CTEs)
- auto-create  `EXTERNAL DATA SOURCE` and `EXTERNAL FILE FORMAT`s.
- [officially rename the adapter from `sqlserver` to `synapse`](https://github.com/swanderz/dbt-synapse/pull/6)
- Use CTAS to create seeds?
- Add support for `ActiveDirectoryMsi`

## Installation
Easiest install is to use pip (not yet registered on PyPI).

First install [ODBC Driver version 17](https://www.microsoft.com/en-us/download/details.aspx?id=56567).

```bash
pip install dbt-synapse
```
On Ubuntu make sure you have the ODBC header files before installing

```
sudo apt install unixodbc-dev
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
  
#### Distributions
- `ROUND_ROBIN` (default)
- `HASH({COLUMN})`
- `REPLICATE`

## example `YAML` for defining external tables
```YAML
sources:
  - name: raw
    schema: source
    loader: ADLSblob
    tables:
      - name: absence_hours
        description: |
          from raw DW.
        external:
          data_source: SynapseContainer
          location: /absence_hours_live/
          file_format: CommaDelimited
          reject_type: VALUE
          reject_value: 0
        columns:
```
# Changelog

See [CHANGELOG.md](CHANGELOG.md)
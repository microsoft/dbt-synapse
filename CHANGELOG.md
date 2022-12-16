# Changelog

## v1.3.2

You can now create seed tables with different distribution and index strategy by providing required confiuration in dbt_project.yml file [#76](https://github.com/dbt-msft/dbt-synapse/issues/76). The default choice is REPLICATE disttribution and HEAP (no indexing). If you want to override this configuration, the following sample should help.

```
name: 'jaffle_shop'
config-version: 2
version: '0.1'
profile: 'jaffle_shop'

seeds:
  jaffle_shop:
    raw_customers_distribution: hash
    raw_customers_hashDistributedColumn: last_name
    raw_customers_index: ci
    raw_customers_ciIndexColumns: id, first_name
    raw_orders_distribution: replicate
    raw_orders_index: heap
    raw_payments_distribution: round_robin
    raw_payments_index: cci

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
analysis-paths: ["analysis"]
macro-paths: ["macros"]

target-path: "target"
clean-targets:
    - "target"
    - "dbt_modules"
    - "logs"

require-dbt-version: [">=1.0.0", "<2.0.0"]

models:
  jaffle_shop:
      materialized: table
      staging:
        materialized: view
```

Create a new dictionary "seeds:" at the root of indendation level and add project name/profile name  "jaffle_shop:" under "seeds:". Add key value pairs under project "jaffle_shop:" to provide distribution and index stratefies 

To specify distribution, use {seed file name}_distribution as a key. Use replicate, round_robin, hash as a value. Example: **raw_customers_distribution: replicate**. The raw_customers seed table will be replicated a table. For hash distribution, the user need to provide has a column to distribute data on. Use {seed file name}_hashDistributedColumn as key and column name as a value. If column name has spaces, then enclose the column name in double quotes. Example: **raw_customers_hashDistributedColumn: last_name**

To specific index, use {seed file name}_index as a key and ci, heap, cci as a value. Example: **raw_customers_index: ci**. The raw_customers seed table will use heap index strategy. For clustered index, the user need to provide one or more columns to create clustered inde on. Use {seed file name}_ciIndexColumns as a key and comma seperated column names. Example: **raw_customers_ciIndexColumns: id, first_name**.

**Note** Multi-column distribution is not supported in this release for seed tables.

## v1.3.1

Integer seed value set to 0 is ingested as a NULL. Bug fix to handle integer seed value when set to 0. [#136](https://github.com/dbt-msft/dbt-synapse/pull/136).

## v1.3.0

Make sure to read the changelog for [dbt-sqlserver 1.3.0](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v1.3.0).

#### Features

* Official compatibility with dbt-core 1.3.0. Python models are not supported in this version.

## v1.2.0

Make sure to read the changelog for [dbt-sqlserver 1.2.0](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v1.2.0).

### Synapse-specific changes

#### Features

* Snapshots with the `merge` strategy now use Synapse's new [`MERGE` statement](https://learn.microsoft.com/en-us/sql/t-sql/statements/merge-transact-sql?view=azure-sqldw-latest&preserve-view=true)

#### Fixes

* Seeds with empty values are now correctly inserted as NULL instead of empty strings.

## v1.1.0

- official release
- see changes in [dbt-sqlserver v1.1.0](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v1.1.0)

## v1.1.0.rc1

- Bump dependencies dbt-sqlserver and dbt-core to 1.1.0
- New testing framework

## v1.0.2

Re-release of v1.0.1 with fixed package.

## v.1.0.1

### Fixes

- re-implement sqlserver's test materialization logic because Synapse adapter can't find it today [#74](https://github.com/dbt-msft/dbt-synapse/pull/74)

## v.1.0.0

Please see the following upstream release notes:
- [dbt-core v1.0.0](https://github.com/dbt-labs/dbt-core/releases/tag/v1.0.0)
- [dbt-sqlserver v1.0.0](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v1.0.0)

## v.0.21.0rc1

Please see the following upstream release notes:
- [dbt-core v0.21.0](https://github.com/dbt-labs/dbt-core/releases/tag/v0.21.0)
- [dbt-sqlserver v0.21.0rc1](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v0.21.0rc1)

## v.0.20.0

### Features

- brings compatibility with dbt-core `v0.20.0`
### Under the hood

- Fix a bug where snapshots on tables with non-indexable datatypes would throw the error `"The statement failed. Column 'XXXXX' has a data type that cannot participate in a columnstore index. (35343) (SQLExecDirectW)"` [#56](https://github.com/dbt-msft/dbt-synapse/pull/56) thanks [MarvinSchenkel](https://github.com/MarvinSchenkel)
- 10+ `synapse__` macros no longer have to be defined as they're now auto-defined as part of the `v0.20.0` upgrade. Code footprint is now >37 lines smaller!

## v.0.19.2

### Under the hood

- fix bug introduced `v0.19.1` where the new macros in [dbt-sqlserver#126](https://github.com/dbt-msft/dbt-sqlserver/pull/126) were still being used somehow
- no longer pin `agate<1.6.2` because it now done as part of [dbt 0.19.1](https://github.com/fishtown-analytics/dbt/releases/tag/v0.19.1)

## v.0.19.1

### Under the hood

- override new functionality in dbt-sqlserver [dbt-sqlserver #126](https://github.com/dbt-msft/dbt-sqlserver/pull/126) that allows for cross-database queries. Azure Synapse does not support this, so `sqlserver__` adapter macros that were previously used by dbt-synapse had to be re-implemented as `synapse__` macros. [#49](https://github.com/dbt-msft/dbt-synapse/pull/49)
- make CI testing auto-start and auto-pause Synapse cluster to save $$$ [#47](https://github.com/dbt-msft/dbt-synapse/pull/47)
## v.0.19.0.1

### Fixes

- Resolves bug where snapshot and seeds materializations weren't working correctly [#45](https://github.com/dbt-msft/dbt-synapse/pull/45) thanks [@alieus]

### Under the hood

- `dbt-synapse` will allow all patches to `dbt-sqlserver` version 0.19
- Per issue with `pyICU` package ([fishtown-analytics/dbt/#3161](https://github.com/fishtown-analytics/dbt/pull/3161)), temporarily pin agate to between `1.6.0` and `1.6.2`, inclusive, until `dbt` `0.19.1` is released.
## v.0.19.0

### BREAKING CHANGES

- you must change your profile so that `type=synapse` instead of `type=sqlserver`. The reason is that now `dbt-synapse` now fully inheirits from `dbt-sqlserver` rather than being a fork. The benefit now is that you can have `dbt-sqlserver` and `dbt-synapse` coexist in the same environment.

### New features:
- Brings support for
  - dbt v0.19.0 ([release notes](https://github.com/fishtown-analytics/dbt/releases/tag/v0.19.0)) and
  - dbt-sqlserver v0.19.0.1 & v0.19.0 ([release](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v0.19.0.1) [notes](https://github.com/dbt-msft/dbt-sqlserver/releases/tag/v0.19.0))

### Under the hood
- the snapshot materialization, except for the [`MERGE` workaround](dbt/include/synapse/macros/materializations/snapshot/snapshot_merge.sql), now depends entirely on dbt-core's global project. Made possible due to tempdb.INFO_SCHEMA workaround [#42](https://github.com/dbt-msft/dbt-synapse/pull/42)
- make the adapter inheirit from `dbt-sqlserver` [#32](https://github.com/dbt-msft/dbt-synapse/pull/32) [#33](https://github.com/dbt-msft/dbt-synapse/pull/33) thanks [@jtcohen6](https://github.com/jtcohen6) [@chaerinlee1](https://github.com/chaerinlee1)
- the snapshot materialization, now depends entirely on dbt-core's global project. See dbt-sqlserver release notes for more info [#44](https://github.com/dbt-msft/dbt-synapse/pull/44)

## v0.18.1
### New Features:
Adds support for:
- SQL Server down to version 2012
- authentication via:
    - Azure CLI (see #71, thanks @JCZuurmond !), and
    - MSFT ODBC Active Directory options (#53 #55 #58 thanks to @NandanHegde15 and @alieus)
- using a named instance (#51 thanks @alangsbo)
- Adds support down to SQL Server 2012
- The adapter is now automatically tested with Fishtowns official adapter-tests to increase stability when making
changes and upgrades to the adapter.

### Fixes:
- Fix for lack of precision in the snapshot check strategy. Previously when executing two check snapshots the same
second, there was inconsistent data as a result. This was mostly noted when running the automatic adapter tests.
NOTE: This fix will create a new snapshot version in the target table
on first run after upgrade.

## v0.18.0.1
### New Features:
- Adds support for Azure Active Directory as authentication provider

### Fixes:
- Fix for lack of precision in the snapshot check strategy. (#74 and #56 thanks @qed) Previously when executing two check snapshots the same second, there was inconsistent data as a result. This was mostly noted when running the automatic adapter tests.
NOTE: This fix will create a new snapshot version in the target table
on first run after upgrade.
- #52 Fix deprecation warning (Thanks @jnoynaert)

### Testing
- The adapter is now automatically tested with Fishtowns official adapter-tests to increase stability when making changes and upgrades to the adapter. (#62 #64 #69 #74)
- We are also now testing specific target configs to make the devs more confident that everything is in working order (#75)

## v0.18.0
### New Features:
- Adds support for dbt v0.18.0

- Add CI testing (#19)
- Remove the external table macros in favor of pulling them directly from `dbt-external-tables`
- Bundle the "`INSERT` & `UPDATE`" `MERGE` workaround into a transaction that can be rolled back (#23)
- Handle nulls in csv file for seeds (#20)
- Verifed that adapter works with `dbt` version `v0.18.1`

## v0.18.0.1
- pull AD auth directly from `dbt-sqlserver` (https://github.com/swanderz/dbt-synapse/pull/13)
- hotfix for broken `create_view()` macro (https://github.com/swanderz/dbt-synapse/pull/14)
- get `dbt-adapter-tests` up and running (https://github.com/swanderz/dbt-synapse/pull/16)
  - make `sqlserver__drop_schema()` also drop all tables and views associated with schema
  - introduce `sqlserver__get_columns_in_query()` for use with testing
  - align macro args with `dbt-base`

## v0.18.0rc2

### Fixes:
- added snapshot functionality

## v0.18.0rc1

### Fixes:
- initial release

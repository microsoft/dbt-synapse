# Changelog
## v1.7.0rc1

## Features

* Support for [dbt-core 1.7](https://github.com/dbt-labs/dbt-core/releases/tag/v1.7.0)
  * implement custom `date_spine` and `generate_series` macro logic for synapse to match nested-CTE limitation

#### Under the hood

  * Decouple `get_catalog` macro (marco override test is skipped as it is not covering the behavior)
  * Add UTF-8-BOM CSV and exclude from precommit format override
  * New/extended adapter test zones
    - get_last_relation_modified
    - date_spine
    - generate_series
    - get_intervals_between
    - get_powers_of_two
    - store_test_failures
    - dbt_clone (same target and state)
    - seed

## v1.6.0rc1

* Support for [dbt-core 1.6](https://github.com/dbt-labs/dbt-core/releases/tag/v1.6.0)

#### Breaking Changes
* Dropped support for Python 3.7 ([#7082](https://github.com/dbt-labs/dbt-core/issues/7082https://github.com/dbt-labs/dbt-core/issues/7082))

## Features
* Add support for materialized views ([#6911](https://github.com/dbt-labs/dbt-core/issues/6911))
  * important note! unlike [dbt's materialized view](https://docs.getdbt.com/docs/build/materializations), [Synapse's materialized view](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-materialized-view-as-select-transact-sql?view=azure-sqldw-latest&context=%2Fazure%2Fsynapse-analytics%2Fcontext%2Fcontext) must be created using aggregation and/or "GROUP BY"! 
* ~~dbt clone ([#7258](https://github.com/dbt-labs/dbt-core/issues/7258)~~ Synapse does not support CLONE)
* Revamp dbt debug ([#7104](https://github.com/dbt-labs/dbt-core/issues/7104))
* Added new adapter zone tests
  - constraints
  - null_compare
  - validate_sql
  - equals
  - dbt_clone

## v.1.5.0rc1

## Features

* Support for [dbt-core 1.5](https://github.com/dbt-labs/dbt-core/releases/tag/v1.5.0)
  * Add support for model contracts by adapting `create_table_as` and `create_view_as` macros

#### Under the hood

  * Define supported constraints in `CONSTRAINT_SUPPORT` Adapter class.
  * Persist docs via [extended properties](https://github.com/dbt-msft/dbt-sqlserver/issues/134) is [not supported](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-addextendedproperty-transact-sql?view=sql-server-ver16) in Synapse
  * Add adapter tests zones
    - caching
    - column_types
    - constraints
    - hooks
    - simple_copy

## v1.4.1rc1

#### Under the hood
* Switch dependency from dbt-sqlserver to dbt-fabric [#441](https://github.com/dbt-msft/dbt-sqlserver/issues/441)
  * for Mac users, before running `make dev`, add `pyodbc==4.0.39 --no-binary :all:` in dev_requirements.txt
  * [Stackoverflow](https://stackoverflow.com/questions/66731036/unable-to-import-pyodbc-on-apple-silicon-symbol-not-found-sqlallochandle) about pyodbc "Symbol not found: _SQLAllocHandle" error

## v1.4.0

#### Features

* Support for [dbt-core 1.4](https://github.com/dbt-labs/dbt-core/releases/tag/v1.4.0)
  * [Incremental predicates](https://docs.getdbt.com/docs/build/incremental-models#about-incremental_predicates)
  * Add support for Python 3.11
  * Replace deprecated exception functions
  * Consolidate timestamp macros

#### Under the hood

* View https://github.com/dbt-msft/dbt-sqlserver/blob/v1.4.latest/CHANGELOG.md#v140 for latest bugfixes in dbt-sqlserver adapter.
* Added all available tests as of dbt 1.4.6

**Full Changelog**: https://github.com/microsoft/dbt-synapse/compare/v1.3.2...v1.4.0

## v1.3.2

You can now create seed tables with different distribution and index strategy by providing required confiuration in dbt_project.yml file [#76](https://github.com/dbt-msft/dbt-synapse/issues/76). The default choice is REPLICATE disttribution and HEAP (no indexing). If you want to override this configuration, the following sample should help.

```
seeds:
  jaffle_shop:
    index: HEAP
    dist: ROUND_ROBIN
    raw_customers:
      index: HEAP
      dist: REPLICATE
    raw_payments:
      dist: HASH(payment_method)
      index: CLUSTERED INDEX(id,order_id)  
```

Create a new context "seeds:" at the root followed by project name and seed name. In this case the project name is jaffle_shop and seeds are raw_customers and raw_payments. Provide index and distribution values using index and dist keys. Use replicate, round_robin, hash({column name}) as a value. Example: **dist: replicate**. The raw_customers seed table will be replicated a table. For hash distribution, the user need to provide the vaule HASH(payment_method). Example: **dist: hash(payment_method)**

To specific index, index as a key and CLUSTERED INDEX({Column1, Column2}), HEAP, CLUSTERED COLUMNSTORE INDEX as a value. Example: **index: HEAP**. The raw_customers seed table will use heap index strategy. For clustered index, the user need to provide one or more columns to create clustered index on. Example: **index: CLUSTERED INDEX(id,order_id)**. The default value of index and distribution can also be set for all seeds under project name.  

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

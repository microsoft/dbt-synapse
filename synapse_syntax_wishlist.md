# Synapse Syntax Wish List

## goal
maximize the amount of common TSQL syntax across:
  - SQL Server 2016+
  - Azure SQL
  - Azure Synapse dedicated pool (ASDP)

In doing this, Azure Data platform delivers:
- lower friction for moving
  - b/w Azure data products, and
  - to Azure data prodcut from competitor's products; and
- a better
  - overall DW dev experience via ASDP (and dbt), and
  - open-source developer experience by reducing the amount of necessaary code to work with all Azure SQL products.

## rationale

The syntactical difference between ANSI SQL PostgreSQL and TSQL is a barrier to entry for new customers to Azure.

Additionally, the intra-TSQL syntax differences are barriers to entry for users coming to ASDP from on-prem SQL Server. Making matters worse, there is no document or cheatsheet published that details the differences and includes workarounds.

Fortunately for dbt users, the dbt-msft adapters, already handle these syntactic features. This means that a dbt project created in Azure SQL can be "migrated" to work on Azure Synapse by changing literally a single YAML parameter (provided the raw source tables already exist).

Nevertheless, a more standard API would greatly reduce friction of moving to and from the above products for ALL TSQL products. Our team already charged though these differences when moving our warehouse to ASDP before we learned of dbt.

Increasingly, data engineering tools are standardizing on SQL as the lingua franca for working with data. We can see this with:
- Synapse's serverless pool which allows querying data lakes with a SQL PI, and
- Databrick's release of SQL Analytics -- which is effectively a SQL DW API on top of delta lake (*`pyspark` and notebooks? never heard of them...*)

One final benefit is that closer API alignment would drastically reduce the code footprint of this adapter. Instead, virtually all macros could be defined once in `dbt-sqlserver`, then be imported. This makes long-term maintenance easier, which, in open-source, is can be a sink-or-swim element.

# Syntax Differences


### [Table Valued Constructor](https://docs.microsoft.com/en-us/sql/t-sql/queries/table-value-constructor-transact-sql)

This is critical for the `dbt seed` command which loads a local csv into the the database.

The difference has brought the dev team [all](https://stackoverflow.com/questions/65625384/why-does-inserting-empty-string-into-date-column-produce-1900-01-01) kinds of problems

#### Azure SQL

```sql
insert into dbo.ceo (id, name, nerd_cred) values
(1, 'Bill Gates', 9),
(2, 'Steve Ballmer', 5),
(3, 'Satyla Nadella', 7);
```

#### Synapse

```sql
insert into dbo.ceo (id, name, nerd_cred)
SELECT 1, 'Bill Gates', 9 UNION ALL
SELECT 2, 'Steve Ballmer', 5 UNION ALL
SELECT 3, 'Satyla Nadella', 7;
```

### `MERGE`

[Uservoice Idea](https://feedback.azure.com/forums/307516-azure-synapse-analytics/suggestions/13520394--in-preview-merge-statement-support)

This is already in public preview, but would love know when it becomes `GA`. When it does, we can drop [`synapse__snapshot_merge_sql`](dbt/include/synapse/macros/materializations/snapshot/snapshot_merge.sql) macro with it's `UPDATE->INSERT` workdaround and rely on [the global project's implementation](https://github.com/fishtown-analytics/dbt/blob/1060035838650a30e86989cbf2693db7720ff002/core/dbt/include/global_project/macros/materializations/snapshot/snapshot_merge.sql#L7-L25)

```sql
{% macro synapse__snapshot_merge_sql(target, source, insert_cols) -%}
      {%- set insert_cols_csv = insert_cols | join(', ') -%}
      EXEC('
           BEGIN TRANSACTION
           update {{ target }}
          set dbt_valid_to = TMP.dbt_valid_to
          from {{ source }} TMP
          where {{ target }}.dbt_scd_id = TMP.dbt_scd_id
            and TMP.dbt_change_type = ''update''
            and {{ target }}.dbt_valid_to is null;

            insert into {{ target }} (
                  {{ insert_cols_csv }}
                  )
            select {{ insert_cols_csv }}
            from {{ source }} 
            where dbt_change_type = ''insert'' ; 
           COMMIT TRANSACTION;
           ');
{% endmacro %}
```
## dropping a view
### `DROP [TABLE/VIEW/SCHEMA/INDEX] ... IF EXISTS`

[relevant Uservoice idea](https://feedback.azure.com/forums/307516-azure-synapse-analytics/suggestions/40068358-temporary-table-get-colunms-informations) ("suggested" 2016, "started" 2018 "planned" 2019)



This one is a lower priority because IMHO, using the first statement enables all the products including SQL Server <2016. Though, the simplicity of the ssecond statement is alluring.
#### Azure Synapse & SQL Server <2016
```sql
-- 
if object_id ('dbo.clippy','V') is not null
  begin
  DROP VIEW dbo.clippy
  end
```
#### Azure SQL & SQL Server >=201
```sql
DROP VIEW dbo.clippy IF EXISTS
```
## Access data from blob
### `OPENROWSET()` vs `CREATE EXTERNAL TABLE()` vs `COPY INTO`
[relevant Uservoice idea](https://feedback.azure.com/forums/307516-azure-synapse-analytics/suggestions/42118774-openrowset-for-dedicated-pools)

These API dicrepancies are painfully confusing.

 because there's two processess that are 80% similar but distinct in different ways.

ASDP supports external tables of type 


## Other Differences

### `tempdb.INFORMATION_SCHEMA.COLUMNS`

[relevant Uservoice idea](https://feedback.azure.com/forums/307516-azure-synapse-analytics/suggestions/40068358-temporary-table-get-colunms-informations) (suggested  Mar 31, 2020)


This introduces challenges for the macro `get_columns_from_relation()`. Basically `get_columns_from_relation` works fine for normal relations becuase we have the normal `INFORMATION_SCHEMA.COLUMNS`. But when the relation is a temp table nothing is returned. 

You can see the discussion in [this PR](https://github.com/dbt-msft/dbt-synapse/pull/40#issuecomment-763502389) in which, we're trying to come up with a robust solution as part of our release for `v0.19.0`.

This breaks the adapter's ability use the snapshot (i.e. SCD type 2) materialization.

The current theory for the best work around is what's sugggested in in [this Stack Overflow post](https://stackoverflow.com/questions/63800841/get-column-names-of-temp-table-in-azure-synapse-dw), which is:
1. if `get_columns_from_relation() is called and the relation is a temp table (i.e. starts with `#`) then:
2. call CTAS to select one from from the temp table
    ```sql
    CREATE TABLE dbo.temp_table_hack AS
    (SELECT TOP(1) * FROM #actual_temp_table )
    ```
3. recursively call `get_columns_from_relation()` on this new table
4. drop the non-temp table

This isn't very pretty, but at least this will dbt users have a frictionless experience moving their dbt projects between TSQL products.


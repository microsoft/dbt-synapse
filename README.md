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

The following is needed for every target definition for both SQL Server and Azure SQL.  The sections below details how to connect to SQL Server and Azure SQL specifically.
```
type: synapse
driver: 'ODBC Driver 17 for SQL Server' (The ODBC Driver installed on your system)
server: server-host-name or ip
port: 1433
schema: schemaname
```

### Security
Encryption is not enabled by default, unless you specify it.

To enable encryption, add the following to your target definition. This is the default encryption strategy recommended by MSFT. For more information see [this docs page](https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/connection-string-syntax#using-trustservercertificate?WT.mc_id=DP-MVP-5003930)
```yaml
encrypt: true # adds "Encrypt=Yes" to connection string
trust_cert: false
```
For a fully-secure, encrypted connection, you must enable `trust_cert: false` because `"TrustServerCertificate=Yes"` is default for `dbt-sqlserver` in order to not break already defined targets. 

### standard SQL Server authentication
SQL Server credentials are supported for on-prem as well as cloud, and it is the default authentication method for `dbt-sqlsever`
```
user: username
password: password
```
### Azure SQL-specific auth
The following [`pyodbc`-supported ActiveDirectory methods](https://docs.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver15#new-andor-modified-dsn-and-connection-string-keywords) are available to authenticate to Azure SQL:
- Azure CLI
- ActiveDirectory Password
- ActiveDirectory Interactive
- ActiveDirectory Integrated
- Service Principal (a.k.a. AAD Application)
- ~~ActiveDirectory MSI~~ (not implemented)

However, the Azure CLI is the ideal way to authenticate instead of using the built-in ODBC ActiveDirectory methods, for reasons detailed below.

#### Azure CLI
Use the authentication of the Azure command line interface (CLI). First, [install the Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli), then, log in:

```bash
az login
```

Then, set `authentication` in `profiles.yml` to `CLI`:

```
authentication: CLI
```

This is also the preferred route for using a service principal:

```
az login --service-principal --username $CLIENTID --password $SECRET --tenant $TENANTID
```

This avoids storing a secret as plain text in `profiles.yml`.

Source: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli#sign-in-using-a-service-principal

#### ActiveDirectory Password 
Definitely not ideal, but available
```
authentication: ActiveDirectoryPassword
user: bill.gates@microsoft.com
password: i<3opensource?
```
#### ActiveDirectory Interactive (*Windows only*)
brings up the Azure AD prompt so you can MFA if need be. The downside to this approach is that you must log in each time you run a dbt command!
```
authentication: ActiveDirectoryInteractive
user: bill.gates@microsoft.com
```
#### ActiveDirectory Integrated (*Windows only*)
uses your machine's credentials (might be disabled by your AAD admins), also requires that you have Active Directory Federation Services (ADFS) installed and running, which is only the case if you have an on-prem Active Directory linked to your Azure AD... 
```
authentication: ActiveDirectoryIntegrated
```
##### Service Principal
`client_*` and `app_*` can be used interchangeably. Again, it is not recommended to store a service principal secret in plain text in your `dbt_profile.yml`. The CLI auth method is preferred.
```
authentication: ServicePrincipal
tenant_id: tenatid
client_id: clientid
client_secret: clientsecret
```

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
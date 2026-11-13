# dbt-synapse

[dbt](https://www.getdbt.com) adapter for Azure Synapse Dedicated SQL Pool (Azure Synapse Data Warehouse).

The adapter supports dbt-core 0.18 or newer and follows the same versioning scheme.
E.g. version 1.1.x of the adapter will be compatible with dbt-core 1.1.x.

## Documentation

We've bundled all documentation on the dbt docs site:

* [Profile setup & authentication](https://docs.getdbt.com/reference/warehouse-profiles/azuresynapse-profile)
* [Adapter-specific configuration](https://docs.getdbt.com/reference/resource-configs/azuresynapse-configs)

Join us on the [dbt Slack](https://getdbt.slack.com/archives/C01DRQ178LQ) to ask questions, get help, or to discuss the project.

## Installation

The adapter connects with [mssql-python](https://github.com/microsoft/mssql-python), the same driver
dbt-fabric uses, so it doesn't need a separately installed ODBC driver. The `driver` and `port`
profile settings are no longer used.

Latest version: ![PyPI](https://img.shields.io/pypi/v/dbt-synapse?label=latest%20stable&logo=pypi)

```shell
pip install -U dbt-synapse
```

Latest pre-release: ![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/v/tag/dbt-msft/dbt-synapse?include_prereleases&label=latest%20pre-release&logo=pypi)

```shell
pip install -U --pre dbt-synapse
```

## Changelog

See [the changelog](CHANGELOG.md)

## Contributing

[![Integration tests on Azure](https://github.com/microsoft/dbt-synapse/actions/workflows/integration-tests-azure.yml/badge.svg)](https://github.com/dbt-msft/dbt-sqlserver/actions/workflows/integration-tests-azure.yml)

This adapter is managed by Microsoft.
You are welcome to contribute by creating issues, opening or reviewing pull requests or helping other users in Slack channel.
If you're unsure how to get started, check out our [contributing guide](CONTRIBUTING.md).

This adapter uses the [dbt-fabric](https://github.com/microsoft/dbt-fabric) adapter underneath so make sure to check out that repository as well.

## License

[![PyPI - License](https://img.shields.io/pypi/l/dbt-synapse)](https://github.com/dbt-msft/dbt-synapse/blob/master/LICENSE)

## Code of Conduct

This project and everyone involved is expected to follow the [dbt Code of Conduct](https://community.getdbt.com/code-of-conduct).

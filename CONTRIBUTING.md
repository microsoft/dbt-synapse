# Development of the adapter

The Synapse adapter uses the [dbt-fabric](https://github.com/microsoft/dbt-fabric) adapter underneath.
This repository mostly contains a set of macros that override the behavior of dbt-fabric so that it works with Synapse.

Python 3.10 is used for developing the adapter. To get started, bootstrap your environment as follows:

Create a virtual environment, [pyenv](https://github.com/pyenv/pyenv) is used in the example:

```shell
pyenv install 3.10.7
pyenv virtualenv 3.10.7 dbt-synapse
pyenv activate dbt-synapse
```

Install the development dependencies and pre-commit and get information about possible make commands:

```shell
make dev  # for Mac users, add `pyodbc==4.0.39 --no-binary :all:` in dev_requirements.txt before running `make dev`
make help
```

[Pre-commit](https://pre-commit.com/) helps us to maintain a consistent style and code quality across the entire project.
After running `make dev`, pre-commit will automatically validate your commits and fix any formatting issues whenever possible.

## Testing

The functional tests require a running Synapse Dedicated SQL Pool instance.
You can configure the connection to this instance with the file `test.env` in the root of the project.
You can use the provided `test.env.sample` as a base.

```shell
cp test.env.sample test.env
```

You can use the following command to run the functional tests:

```shell
make functional
```

## CI/CD

We use Docker images that have all the things we need to test the adapter in the CI/CD workflows.
The Dockerfile and image are part of the [dbt-sqlserver](https://github.com/dbt-msft/dbt-sqlserver) repository.

All CI/CD pipelines are using GitHub Actions. The following pipelines are available:

* `integration-tests-azure`: runs the integration tests for Azure SQL Server.
* `release-version`: publishes the adapter to PyPI.

There is an additional [Pre-commit](https://pre-commit.ci/) pipeline that validates the code style.

### Azure integration tests

The following environment variables are available:

* `DBT_SYNAPSE_SERVER`: Name of the Synapse workspace
* `DBT_SYNAPSE_DB`: Name of the Synapse dedicated SQL pool
* `DBT_AZURE_TENANT`: Azure tenant ID
* `DBT_AZURE_SUBSCRIPTION_ID`: Azure subscription ID
* `DBT_AZURE_RESOURCE_GROUP_NAME`: Azure resource group name
* `DBT_AZURE_SP_NAME`: Client/application ID of the service principal used to connect to Azure AD
* `DBT_AZURE_SP_SECRET`: Password of the service principal used to connect to Azure AD

## Releasing a new version

Make sure the version number is bumped in `__version__.py`. Then, create a git tag named `v<version>` and push it to GitHub.
A GitHub Actions workflow will be triggered to build the package and push it to PyPI.

Make sure that the dependency to dbt-fabric is bumped to a compatible version in `setup.py`.

If you're releasing support for a new version of `dbt-core`, also bump the `dbt_version` in `setup.py`.

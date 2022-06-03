import os

import pytest

pytest_plugins = ["dbt.tests.fixtures.project"]


def pytest_addoption(parser):
    parser.addoption("--profile", action="store", default="user", type=str)


@pytest.fixture(scope="class")
def dbt_profile_target(request):
    profile = request.config.getoption("--profile")

    if profile == "ci_azure_auto":
        return _profile_ci_azure_auto()
    if profile == "user":
        return _profile_user()

    raise ValueError(f"Unknown profile: {profile}")


def _all_profiles_base():
    return {
        "type": "synapse",
        "threads": 1,
        "driver": "ODBC Driver 17 for SQL Server",
        "port": 1433,
        "encrypt": True,
        "trust_cert": True,
    }


def _profile_ci_azure_auto():
    return {
        **_all_profiles_base(),
        **{
            "authentication": "auto",
            "host": os.getenv("DBT_AZURESQL_SERVER"),
            "database": os.getenv("DBT_AZURESQL_DB"),
        },
    }


def _profile_user():
    return {
        **_all_profiles_base(),
        **{
            "driver": os.getenv("SYNAPSE_TEST_DRIVER"),
            "host": os.getenv("SYNAPSE_TEST_HOST"),
            "port": int(os.getenv("SYNAPSE_TEST_PORT")),
            "user": os.getenv("SYNAPSE_TEST_USER"),
            "pass": os.getenv("SYNAPSE_TEST_PASS"),
            "database": os.getenv("SYNAPSE_TEST_DWH_NAME"),
        },
    }


@pytest.fixture(autouse=True)
def skip_by_profile_type(request):
    profile_type = request.config.getoption("--profile")
    if request.node.get_closest_marker("skip_profile"):
        for skip_profile_type in request.node.get_closest_marker("skip_profile").args:
            if skip_profile_type == profile_type:
                pytest.skip("Skipped on '{profile_type}' profile")

#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup
import os
import re

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


package_name = "dbt-synapse"
authors_list = ["Nandan Hegde", "Chaerin Lee", "Alieu Sanneh", "Anders Swanson"]


# get this from a separate file
def _dbt_synapse_version():
    _version_path = os.path.join(
        this_directory, 'dbt', 'adapters', 'synapse', '__version__.py'
    )
    _version_pattern = r'''version\s*=\s*["'](.+)["']'''
    with open(_version_path) as f:
        match = re.search(_version_pattern, f.read().strip())
        if match is None:
            raise ValueError(f'invalid version at {_version_path}')
        return match.group(1)


package_version = _dbt_synapse_version()
description = """An Azure Synapse adpter plugin for dbt (data build tool)"""

dbt_version = '0.19'
# the package version should be the dbt version, with maybe some things on the
# ends of it. (0.18.1 vs 0.18.1a1, 0.18.1.1, ...)
if not package_version.startswith(dbt_version):
    raise ValueError(
        f'Invalid setup.py: package_version={package_version} must start with '
        f'dbt_version={dbt_version}'
    )

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    long_description_content_type="text/markdown",
    license="MIT",
    author=", ".join(authors_list),
    author_email="swanson.anders@gmail.com",
    url="https://github.com/dbt-msft/dbt-synapse",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "dbt-sqlserver>=0.19.1,<0.20.0"
    ]
)

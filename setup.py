#!/usr/bin/env python
import os
import re
import sys

from setuptools import find_namespace_packages, setup
from setuptools.command.install import install

package_name = "dbt-synapse"
authors_list = [
    "Pradeep Srikakolapu",
    "Nandan Hegde",
    "Chaerin Lee",
    "Alieu Sanneh",
    "Anders Swanson",
    "Sam Debruyn",
]
dbt_fabric_requirement = "dbt-fabric>=1.8.6,<2.0"
description = """An Azure Synapse adapter plugin for dbt"""

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as f:
    long_description = f.read()


# get this from a separate file
def _dbt_synapse_version():
    _version_path = os.path.join(this_directory, "dbt", "adapters", "synapse", "__version__.py")
    _version_pattern = r"""version\s*=\s*["'](.+)["']"""
    with open(_version_path) as f:
        match = re.search(_version_pattern, f.read().strip())
        if match is None:
            raise ValueError(f"invalid version at {_version_path}")
        return match.group(1)


package_version = _dbt_synapse_version()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "Verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("GITHUB_REF_NAME")
        tag_without_prefix = tag[1:]

        if tag_without_prefix != package_version:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag_without_prefix, package_version
            )
            sys.exit(info)


setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author=", ".join(authors_list),
    url="https://github.com/microsoft/dbt-synapse",
    packages=find_namespace_packages(include=["dbt", "dbt.*"]),
    include_package_data=True,
    install_requires=[dbt_fabric_requirement],
    cmdclass={
        "verify": VerifyVersionCommand,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

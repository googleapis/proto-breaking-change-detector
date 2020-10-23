# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import os

from setuptools import find_packages, setup  # type: ignore


PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

version = "1.0.0"

with io.open(os.path.join(PACKAGE_ROOT, "README.md")) as file_obj:
    README = file_obj.read()

setup(
    name="proto-breaking-change-detector",
    version=version,
    license="Apache 2.0",
    author="Xiaozhen Liu",
    author_email="xiaozhenliu@google.com",
    url="https://github.com/googleapis/proto-breaking-change-detector.git",
    packages=find_packages(),
    description="Breaking change detector that takes API proto definition files and detects the unintended breaking changes in minor versions updates.",
    long_description=README,
    platforms="Linux",
    include_package_data=True,
    install_requires=(
        "googleapis-common-protos >= 1.6.0",
        "protobuf >= 3.12.0",
    ),
    extras_require={
        ':python_version<"3.7"': ("dataclasses >= 0.4",),
    },
    python_requires=">=3.6",
    classifiers=(
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Breaking Change Detectors",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
    zip_safe=False,
)

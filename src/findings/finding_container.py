# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from src.findings.utils import Finding
from src.findings.utils import FindingCategory


class FindingContainer:
    _finding_results = []

    @classmethod
    def addFinding(
        cls,
        category: FindingCategory,
        proto_file_name: str,
        source_code_line: int,
        message: str,
        actionable: bool,
        extra_info=None,
    ):
        cls._finding_results.append(
            Finding(
                category,
                proto_file_name,
                source_code_line,
                message,
                actionable,
                extra_info,
            )
        )

    @classmethod
    def getAllFindings(cls):
        return cls._finding_results

    @classmethod
    def toJson(cls):
        findingDictArr = []
        for finding in cls._finding_results:
            findingDictArr.append(finding.toDict())
        return json.dumps(findingDictArr)

    @classmethod
    def reset(cls):
        cls._finding_results = []

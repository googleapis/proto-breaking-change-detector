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
    def getActionableFindings(cls):
        return [finding for finding in cls._finding_results if finding.actionable]

    @classmethod
    def toHumanReadableMessage(cls):
        output_message = ""
        file_to_findings = {}
        for finding in cls.getActionableFindings():
            # Create a map to summarize the findings based on proto file name.
            if finding.location.proto_file_name not in file_to_findings:
                file_to_findings[finding.location.proto_file_name] = []
            file_to_findings[finding.location.proto_file_name].append(finding)
        # Add each finding to the output message.
        for file_name in file_to_findings:
            # Customize sort key function to output the findings in the same
            # file based on the source code line number.
            def _get_line_number(finding):
                return finding.location.source_code_line

            file_to_findings[file_name].sort(key=_get_line_number)
            for finding in file_to_findings[file_name]:
                output_message += f"{file_name} L{finding.location.source_code_line}: {finding.message}\n"
        return output_message

    @classmethod
    def toJson(cls):
        findingDictArr = []
        for finding in cls._finding_results:
            findingDictArr.append(finding.toDict())
        return json.dumps(findingDictArr)

    @classmethod
    def reset(cls):
        cls._finding_results = []

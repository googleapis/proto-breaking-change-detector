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

from src.findings.utils import Finding
from src.findings.utils import FindingCategory
from collections import defaultdict


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
    def toDictArr(cls):
        return [finding.toDict() for finding in cls._finding_results]

    @classmethod
    def toHumanReadableMessage(cls):
        output_message = ""
        file_to_findings = defaultdict(list)
        for finding in cls.getActionableFindings():
            # Create a map to summarize the findings based on proto file name.s
            file_to_findings[finding.location.proto_file_name].append(finding)
        # Add each finding to the output message.
        for file_name, findings in file_to_findings.items():
            # Customize sort key function to output the findings in the same
            # file based on the source code line number.
            findings.sort(key=lambda f: f.location.source_code_line)
            for finding in findings:
                output_message += f"{file_name} L{finding.location.source_code_line}: {finding.message}\n"
        return output_message

    @classmethod
    def reset(cls):
        cls._finding_results = []

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

from src.findings.utils import FindingCategory, ChangeType, Finding
from collections import defaultdict


class FindingContainer:
    def __init__(self):
        self.finding_results = []

    def addFinding(
        self,
        category: FindingCategory,
        proto_file_name: str,
        source_code_line: int,
        message: str,
        change_type: ChangeType,
        extra_info=None,
    ):
        self.finding_results.append(
            Finding(
                category,
                proto_file_name,
                source_code_line,
                message,
                change_type,
                extra_info,
            )
        )

    def getAllFindings(self):
        return self.finding_results

    def getActionableFindings(self):
        return [
            finding
            for finding in self.finding_results
            if finding.change_type == ChangeType.MAJOR
        ]

    def toDictArr(self):
        return [finding.toDict() for finding in self.finding_results]

    def toHumanReadableMessage(self):
        output_message = ""
        file_to_findings = defaultdict(list)
        for finding in self.getActionableFindings():
            # Create a map to summarize the findings based on proto file name.s
            file_to_findings[finding.location.proto_file_name].append(finding)
        # Add each finding to the output message.
        for file_name, findings in file_to_findings.items():
            # Customize sort key function to output the findings in the same
            # file based on the source code line number.
            # Sort message alphabetically if the line number is same.
            findings.sort(key=lambda f: (f.location.proto_file_name, f.location.source_code_line, f.message))
            for finding in findings:
                output_message += f"{file_name} L{finding.location.source_code_line}: {finding.message}\n"
        return output_message

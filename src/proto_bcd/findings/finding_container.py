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

from re import sub
from typing import Callable
from proto_bcd.findings.finding import Finding
from proto_bcd.findings.finding_category import (
    FindingCategory,
    ChangeType,
    ConventionalCommitTag,
)
from collections import defaultdict


def sorted_filtered_findings(findings: list, filter: Callable) -> list:
    filtered = [f for f in findings if filter(f)]
    filtered.sort(
        key=lambda f: (
            f.location.proto_file_name,
            f.location.source_code_line,
            f.subject,
            f.oldsubject,
            f.context,
            f.type,
            f.oldtype,
        )
    )
    return filtered


class FindingContainer:
    def __init__(self):
        self.finding_results = []

    def add_finding(
        self,
        category: FindingCategory,
        proto_file_name: str,
        source_code_line: int,
        conventional_commit_tag: ConventionalCommitTag,
        change_type=ChangeType.UNDEFINED,
        extra_info=None,
        subject="",
        oldsubject="",
        context="",
        type="",
        oldtype="",
        oldcontext="",
    ):
        if change_type == ChangeType.UNDEFINED:
            if (
                conventional_commit_tag == ConventionalCommitTag.FEAT_BREAKING
                or conventional_commit_tag == ConventionalCommitTag.FIX_BREAKING
            ):
                change_type = ChangeType.MAJOR
            elif conventional_commit_tag == ConventionalCommitTag.FEAT:
                change_type = ChangeType.MINOR
            elif conventional_commit_tag == ConventionalCommitTag.FIX:
                change_type = ChangeType.PATCH
            else:
                change_type = ChangeType.NONE

        self.finding_results.append(
            Finding(
                category=category,
                proto_file_name=proto_file_name,
                source_code_line=source_code_line,
                change_type=change_type,
                conventional_commit_tag=conventional_commit_tag,
                extra_info=extra_info,
                subject=subject,
                oldsubject=oldsubject,
                context=context,
                type=type,
                oldtype=oldtype,
                oldcontext=oldcontext,
            )
        )

    def get_all_findings(self):
        return sorted_filtered_findings(self.finding_results, lambda f: True)

    def get_actionable_findings(self):
        return sorted_filtered_findings(
            self.finding_results, lambda f: f.change_type == ChangeType.MAJOR
        )

    def to_dict_arr(self):
        return [finding.to_dict() for finding in self.finding_results]

    def to_human_readable_message(self, line_numbers=True, all_changes=False):
        output_message = ""
        file_to_findings = defaultdict(list)
        if all_changes:
            findings = self.get_all_findings()
        else:
            findings = self.get_actionable_findings()
        for finding in findings:
            # Create a map to summarize the findings based on proto file name.
            file_to_findings[finding.location.proto_file_name].append(finding)
        # Add each finding to the output message.
        for file_name, findings in file_to_findings.items():
            # Customize sort key function to output the findings in the same
            # file based on the source code line number.
            # Sort message alphabetically if the line number is same.
            sorted_findings = sorted_filtered_findings(findings, lambda f: True)
            for finding in sorted_findings:
                message = finding.get_message()
                if finding.location.source_code_line == -1 or not line_numbers:
                    output_message += f"{file_name}: {message}\n"
                else:
                    output_message += (
                        f"{file_name} L{finding.location.source_code_line}: {message}\n"
                    )
        return output_message

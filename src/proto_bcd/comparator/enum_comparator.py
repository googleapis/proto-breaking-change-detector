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

from proto_bcd.comparator.enum_value_comparator import EnumValueComparator
from proto_bcd.findings.finding_container import FindingContainer
from proto_bcd.findings.finding_category import (
    FindingCategory,
    ConventionalCommitTag,
)
from proto_bcd.comparator.wrappers import Enum


class EnumComparator:
    def __init__(
        self,
        enum_original: Enum,
        enum_update: Enum,
        finding_container: FindingContainer,
        context: str,
    ):
        self.enum_original = enum_original
        self.enum_update = enum_update
        self.finding_container = finding_container
        self.context = context

    def compare(self):
        # 1. If the original EnumDescriptor is None,
        # then a new EnumDescriptor is added.
        if self.enum_original is None:
            self.finding_container.add_finding(
                category=FindingCategory.ENUM_ADDITION,
                proto_file_name=self.enum_update.proto_file_name,
                source_code_line=self.enum_update.source_code_line,
                subject=self.enum_update.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FEAT,
            )

        # 2. If the updated EnumDescriptor is None,
        # then the original EnumDescriptor is removed.
        elif self.enum_update is None:
            self.finding_container.add_finding(
                category=FindingCategory.ENUM_REMOVAL,
                proto_file_name=self.enum_original.proto_file_name,
                source_code_line=self.enum_original.source_code_line,
                subject=self.enum_original.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
            )

        # 3. If the EnumDescriptors have the same name, check the values
        # of them stay the same. Enum values are identified by number.
        else:
            enum_values_dict_original = self.enum_original.values
            enum_values_dict_update = self.enum_update.values
            enum_values_keys_set_original = set(enum_values_dict_original.keys())
            enum_values_keys_set_update = set(enum_values_dict_update.keys())
            # Compare Enum values that only exist in the original version.
            for name in enum_values_keys_set_original - enum_values_keys_set_update:
                EnumValueComparator(
                    enum_values_dict_original[name],
                    None,
                    self.finding_container,
                    context=self.enum_update.name,
                ).compare()
            # Compare Enum values that only exist in the update version.
            for name in enum_values_keys_set_update - enum_values_keys_set_original:
                EnumValueComparator(
                    None,
                    enum_values_dict_update[name],
                    self.finding_container,
                    context=self.enum_update.name,
                ).compare()
            # Compare Enum values that exist in both original and update versions.
            for name in enum_values_keys_set_original & enum_values_keys_set_update:
                EnumValueComparator(
                    enum_values_dict_original[name],
                    enum_values_dict_update[name],
                    self.finding_container,
                    context=self.enum_update.name,
                ).compare()

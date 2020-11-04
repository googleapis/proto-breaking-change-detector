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

from src.comparator.enum_value_comparator import EnumValueComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory
from src.comparator.wrappers import Enum


class EnumComparator:
    def __init__(self, enum_original: Enum, enum_update: Enum):
        self.enum_original = enum_original
        self.enum_update = enum_update

    def compare(self):
        # 1. If original EnumDescriptor is None, then a new
        # EnumDescriptor is added.
        if self.enum_original is None:
            FindingContainer.addFinding(
                category=FindingCategory.ENUM_ADDITION,
                proto_file_name=self.enum_update.proto_file_name,
                source_code_line=self.enum_update.source_code_line,
                message=f"A new Enum {self.enum_update.name} is added.",
                actionable=False,
            )

        # 2. If updated EnumDescriptor is None, then the original
        # EnumDescriptor is removed.
        elif self.enum_update is None:
            FindingContainer.addFinding(
                category=FindingCategory.ENUM_REMOVAL,
                proto_file_name=self.enum_original.proto_file_name,
                source_code_line=self.enum_original.source_code_line,
                message=f"An Enum {self.enum_original.name} is removed",
                actionable=True,
            )

        # 3. If the EnumDescriptors have the same name, check the values
        # of them stay the same. Enum values are identified by number,
        # not by name.
        else:
            enum_values_dict_original = self.enum_original.values
            enum_values_dict_update = self.enum_update.values
            enum_values_keys_set_original = set(enum_values_dict_original.keys())
            enum_values_keys_set_update = set(enum_values_dict_update.keys())
            # Compare Enum values that only exist in original version
            for number in enum_values_keys_set_original - enum_values_keys_set_update:
                EnumValueComparator(enum_values_dict_original[number], None).compare()
            # Compare Enum values that only exist in update version
            for number in enum_values_keys_set_update - enum_values_keys_set_original:
                EnumValueComparator(None, enum_values_dict_update[number]).compare()
            # Compare Enum values that exist both in original and update versions
            for number in enum_values_keys_set_original & enum_values_keys_set_update:
                EnumValueComparator(
                    enum_values_dict_original[number], enum_values_dict_update[number]
                ).compare()

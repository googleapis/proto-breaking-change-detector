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

from google.protobuf.descriptor_pb2 import EnumValueDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class EnumValueComparator:
    def __init__(
        self,
        enum_value_original: EnumValueDescriptorProto,
        enum_value_update: EnumValueDescriptorProto,
    ):
        self.enum_value_original = enum_value_original
        self.enum_value_update = enum_value_update

    def compare(self):
        # 1. If original EnumValue is None, then a new EnumValue is added.
        if self.enum_value_original is None:
            msg = "A new EnumValue {} is added.".format(self.enum_value_update.name)
            FindingContainer.addFinding(
                FindingCategory.ENUM_VALUE_ADDITION, "", msg, False
            )
        # 2. If updated EnumValue is None, then the original EnumValue is removed.
        elif self.enum_value_update is None:
            msg = "An EnumValue {} is removed".format(self.enum_value_original.name)
            FindingContainer.addFinding(
                FindingCategory.ENUM_VALUE_REMOVAL, "", msg, True
            )
        # 3. If both EnumValueDescriptors are existing, check if the name is changed.
        elif self.enum_value_original.name != self.enum_value_update.name:
            msg = "Name of the EnumValue is changed, the original is {}, but the updated is {}".format(
                self.enum_value_original.name, self.enum_value_update.name
            )
            FindingContainer.addFinding(
                FindingCategory.ENUM_VALUE_NAME_CHANGE, "", msg, True
            )

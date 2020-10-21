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

from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class FieldComparator:
    def __init__(
        self, field_original: FieldDescriptorProto, field_update: FieldDescriptorProto
    ):
        self.field_original = field_original
        self.field_update = field_update

    def compare(self):
        # 1. If original FieldDescriptor is None, then a
        # new FieldDescriptor is added.
        if self.field_original is None:
            msg = f"A new Field {self.field_update.name} is added."
            FindingContainer.addFinding(FindingCategory.FIELD_ADDITION, "", msg, False)
            return

        # 2. If updated FieldDescriptor is None, then
        # the original FieldDescriptor is removed.
        if self.field_update is None:
            msg = f"A Field {self.field_original.name} is removed"
            FindingContainer.addFinding(FindingCategory.FIELD_REMOVAL, "", msg, True)
            return

        # 3. If both FieldDescriptors are existing, check
        # if the name is changed.
        if self.field_original.name != self.field_update.name:
            msg = f"Name of the Field is changed, the original is {self.field_original.name}, but the updated is {self.field_update.name}"
            FindingContainer.addFinding(
                FindingCategory.FIELD_NAME_CHANGE, "", msg, True
            )
            return

        # 4. If the EnumDescriptors have the same name, check if the
        # repeated state of them stay the same.
        if self.field_original.label != self.field_update.label:
            option_original = FieldDescriptorProto().Label.Name(
                self.field_original.label
            )
            option_update = FieldDescriptorProto().Label.Name(self.field_update.label)
            msg = f"Repeated state of the Field is changed, the original is {option_original}, but the updated is {option_update}"
            FindingContainer.addFinding(
                FindingCategory.FIELD_REPEATED_CHANGE, "", msg, True
            )

        # 5. If the EnumDescriptors have the same repeated state,
        # check if the type of them stay the same.
        if self.field_original.type != self.field_update.type:
            type_original = FieldDescriptorProto().Type.Name(self.field_original.type)
            type_update = FieldDescriptorProto().Type.Name(self.field_update.type)
            msg = f"Type of the field is changed, the original is {type_original}, but the updated is {type_update}"
            FindingContainer.addFinding(
                FindingCategory.FIELD_TYPE_CHANGE, "", msg, True
            )

        # 6. Check `google.api.resource_reference` annotation.
        # TODO(xiaozhenliu): annotation is removed, but the using
        # file-level resource is added to the message.
        # This should not be taken as breaking change.

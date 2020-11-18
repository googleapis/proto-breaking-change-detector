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

from src.comparator.field_comparator import FieldComparator
from src.comparator.enum_comparator import EnumComparator
from src.comparator.wrappers import Message
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class DescriptorComparator:
    def __init__(
        self,
        message_original: Message,
        message_update: Message,
        finding_container: FindingContainer,
    ):
        self.message_original = message_original
        self.message_update = message_update
        self.finding_container = finding_container

    def compare(self):
        # _compare method will be recursively called for nested message comparison.
        self._compare(self.message_original, self.message_update)

    def _compare(self, message_original, message_update):
        # 1. If original message is None, then a new message is added.
        if message_original is None:
            self.finding_container.addFinding(
                category=FindingCategory.MESSAGE_ADDITION,
                proto_file_name=message_update.proto_file_name,
                source_code_line=message_update.source_code_line,
                message=f"A new message `{message_update.name}` is added.",
                actionable=False,
            )
            return
        # 2. If updated message is None, then the original message is removed.
        if message_update is None:
            self.finding_container.addFinding(
                category=FindingCategory.MESSAGE_REMOVAL,
                proto_file_name=message_original.proto_file_name,
                source_code_line=message_original.source_code_line,
                message=f"An existing message `{message_original.name}` is removed.",
                actionable=True,
            )
            return

        self.global_resources_original = self.message_original.file_resources
        self.global_resources_update = self.message_update.file_resources
        # 3. Check breaking changes in each fields. Note: Fields are
        # identified by number, not by name. Descriptor.fields_by_number
        # (dict int -> FieldDescriptor) indexed by number.
        if message_original.fields or message_update.fields:
            self._compare_nested_fields(
                message_original.fields,
                message_update.fields,
            )

        # 4. Check breaking changes in nested message.
        # Descriptor.nested_types_by_name (dict str -> Descriptor)
        # indexed by name. Recursively call _compare for nested
        # message type comparison.
        if message_original.nested_messages or message_update.nested_messages:
            self._compare_nested_messages(
                message_original.nested_messages,
                message_update.nested_messages,
            )
        # 5. Check breaking changes in nested enum.
        if message_original.nested_enums or message_update.nested_enums:
            self._compare_nested_enums(
                message_original.nested_enums,
                message_update.nested_enums,
            )

        # 6. Check `google.api.resource` annotation.
        self._compare_resources(message_original.resource, message_update.resource)

    def _compare_nested_fields(self, fields_dict_original, fields_dict_update):
        fields_number_original = set(fields_dict_original.keys())
        fields_number_update = set(fields_dict_update.keys())

        for fieldNumber in fields_number_original - fields_number_update:
            FieldComparator(
                fields_dict_original[fieldNumber],
                None,
                self.finding_container,
            ).compare()
        for fieldNumber in fields_number_update - fields_number_original:
            FieldComparator(
                None,
                fields_dict_update[fieldNumber],
                self.finding_container,
            ).compare()
        for fieldNumber in fields_number_original & fields_number_update:
            FieldComparator(
                fields_dict_original[fieldNumber],
                fields_dict_update[fieldNumber],
                self.finding_container,
            ).compare()

    def _compare_nested_messages(
        self, nested_msg_dict_original, nested_msg_dict_update
    ):
        message_name_original = set(nested_msg_dict_original.keys())
        message_name_update = set(nested_msg_dict_update.keys())

        for msgName in message_name_original - message_name_update:
            self._compare(nested_msg_dict_original[msgName], None)
        for msgName in message_name_update - message_name_original:
            self._compare(None, nested_msg_dict_update[msgName])
        for msgName in message_name_update & message_name_original:
            self._compare(
                nested_msg_dict_original[msgName],
                nested_msg_dict_update[msgName],
            )

    def _compare_nested_enums(self, nested_enum_dict_original, nested_enum_dict_update):
        enum_name_original = set(nested_enum_dict_original.keys())
        enum_name_update = set(nested_enum_dict_update.keys())

        for name in enum_name_original - enum_name_update:
            EnumComparator(nested_enum_dict_original[name], None).compare()
        for name in enum_name_update - enum_name_original:
            EnumComparator(None, nested_enum_dict_update[name]).compare()
        for name in enum_name_original & enum_name_update:
            EnumComparator(
                nested_enum_dict_original[name],
                nested_enum_dict_update[name],
                self.finding_container,
            ).compare()

    def _compare_resources(
        self,
        resource_original,
        resource_update,
    ):
        if not resource_original and not resource_update:
            return
        # 1. A new resource definition is added.
        if not resource_original and resource_update:
            self.finding_container.addFinding(
                category=FindingCategory.RESOURCE_DEFINITION_ADDITION,
                proto_file_name=self.message_update.proto_file_name,
                source_code_line=resource_update.source_code_line,
                message=f"A message-level resource definition `{resource_update.value.type}` has been added.",
                actionable=False,
            )
            return
        # 2. Message-level resource definitions removal may not be breaking change since
        # the resource could be moved to file-level resource definition.
        # 3. Note that the type change of an existing resource definition is like one resource
        # is removed and another one is added.
        if (resource_original and not resource_update) or (
            resource_original.value.type != resource_update.value.type
        ):
            if not self.global_resources_update:
                self.finding_container.addFinding(
                    category=FindingCategory.RESOURCE_DEFINITION_REMOVAL,
                    proto_file_name=self.message_original.proto_file_name,
                    source_code_line=resource_original.source_code_line,
                    message=f"An existing message-level resource definition `{resource_original.value.type}` has been removed.",
                    actionable=True,
                )
                return
            # Check if the removed resource is in the global file-level resource database.
            if resource_original.value.type not in self.global_resources_update.types:
                self.finding_container.addFinding(
                    category=FindingCategory.RESOURCE_DEFINITION_REMOVAL,
                    proto_file_name=self.message_original.proto_file_name,
                    source_code_line=resource_original.source_code_line,
                    message=f"An existing message-level resource definition `{resource_original.value.type}` has been removed.",
                    actionable=True,
                )
            else:
                # Check the patterns of existing file-level resource are compatible with
                # the patterns of the removed message-level resource.
                global_resource_pattern = self.global_resources_update.types[
                    resource_original.value.type
                ].value.pattern

                # If there is pattern removal, or pattern value change. Then the global file-level resource
                # can not replace the original message-level resource.
                if self._compatible_patterns(
                    resource_original.value.pattern, global_resource_pattern
                ):
                    self.finding_container.addFinding(
                        category=FindingCategory.RESOURCE_DEFINITION_REMOVAL,
                        proto_file_name=self.message_original.proto_file_name,
                        source_code_line=resource_original.source_code_line,
                        message=f"An existing message-level resource definition `{resource_original.value.type}` has been removed.",
                        actionable=True,
                    )
            return
        # Resource is existing in both original and update versions.
        # 3. Patterns of message-level resource definitions have changed.
        if not self._compatible_patterns(
            resource_original.value.pattern, resource_update.value.pattern
        ):
            self.finding_container.addFinding(
                category=FindingCategory.RESOURCE_DEFINITION_CHANGE,
                proto_file_name=self.message_update.proto_file_name,
                source_code_line=resource_update.source_code_line,
                message=f"The pattern of an existing message-level resource definition `{resource_original.value.type}` has changed from `{resource_original.value.pattern}` to `{resource_update.value.pattern}`.",
                actionable=True,
            )

    def _compatible_patterns(self, patterns_original, patterns_update):
        # An existing pattern is removed.
        if len(patterns_original) > len(patterns_update):
            return False
        # An existing pattern value is changed.
        for old_pattern, new_pattern in zip(patterns_original, patterns_update):
            if old_pattern != new_pattern:
                return False
        return True

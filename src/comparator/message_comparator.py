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
from src.findings.utils import FindingCategory, ChangeType


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
        if not message_update and not message_original:
            return
        # 1. If original message is None, then a new message is added.
        if message_original is None and message_update:
            self.finding_container.addFinding(
                category=FindingCategory.MESSAGE_ADDITION,
                proto_file_name=message_update.proto_file_name,
                source_code_line=message_update.source_code_line,
                message=f"A new message `{message_update.name}` is added.",
                change_type=ChangeType.MINOR,
            )
        # 2. If updated message is None, then the original message is removed.
        elif message_update is None and message_original:
            self.finding_container.addFinding(
                category=FindingCategory.MESSAGE_REMOVAL,
                proto_file_name=message_original.proto_file_name,
                source_code_line=message_original.source_code_line,
                message=f"An existing message `{message_original.name}` is removed.",
                change_type=ChangeType.MAJOR,
            )
        else:
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
            # Enums are identified by names.
            if message_original.nested_enums or message_update.nested_enums:
                self._compare_nested_enums(
                    message_original.nested_enums,
                    message_update.nested_enums,
                )

            # 6. Check `google.api.resource` annotation.
            # This check has been done in file_set comparator. Since we have
            # registered all resources in the database.

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
            EnumComparator(
                nested_enum_dict_original[name],
                None,
                self.finding_container,
            ).compare()
        for name in enum_name_update - enum_name_original:
            EnumComparator(
                None,
                nested_enum_dict_update[name],
                self.finding_container,
            ).compare()
        for name in enum_name_original & enum_name_update:
            EnumComparator(
                nested_enum_dict_original[name],
                nested_enum_dict_update[name],
                self.finding_container,
            ).compare()

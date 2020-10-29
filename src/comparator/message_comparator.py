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

from google.api import resource_pb2
from google.protobuf.descriptor_pb2 import DescriptorProto
from src.comparator.field_comparator import FieldComparator
from src.comparator.resource_database import ResourceDatabase
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class DescriptorComparator:
    def __init__(
        self,
        message_original: DescriptorProto,
        message_update: DescriptorProto,
        global_resources_original=None,
        global_resources_update=None,
    ):
        self.message_original = message_original
        self.message_update = message_update
        self.global_resources_original = global_resources_original
        self.global_resources_update = global_resources_update

    def compare(self):
        # _compare method will be recursively called for nested message comparison.
        self._compare(self.message_original, self.message_update)

    def _compare(self, message_original, message_update):
        # 1. If original message is None, then a new message is added.
        if message_original is None:
            msg = f"A new message {message_update.name} is added."
            FindingContainer.addFinding(
                FindingCategory.MESSAGE_ADDITION, "", msg, False
            )
            return
        # 2. If updated message is None, then the original message is removed.
        if message_update is None:
            msg = f"A message {message_original.name} is removed"
            FindingContainer.addFinding(FindingCategory.MESSAGE_REMOVAL, "", msg, True)
            return

        # 3. Check breaking changes in each fields. Note: Fields are
        # identified by number, not by name. Descriptor.fields_by_number
        # (dict int -> FieldDescriptor) indexed by number.
        if message_original.field or message_update.field:
            self._compareNestedFields(
                {f.number: f for f in message_original.field},
                {f.number: f for f in message_update.field},
            )

        # 4. Check breaking changes in nested message.
        # Descriptor.nested_types_by_name (dict str -> Descriptor)
        # indexed by name. Recursively call _compare for nested
        # message type comparison.
        if message_original.nested_type or message_update.nested_type:
            self._compareNestedMessages(
                {m.name: m for m in message_original.nested_type},
                {m.name: m for m in message_update.nested_type},
            )

        # 5. Check `google.api.resource` annotation.
        self._compareResources(message_original, message_update)

    def _compareNestedFields(self, fields_dict_original, fields_dict_update):
        fields_number_original = set(fields_dict_original.keys())
        fields_number_update = set(fields_dict_update.keys())

        for fieldNumber in fields_number_original - fields_number_update:
            FieldComparator(fields_dict_original[fieldNumber], None).compare()
        for fieldNumber in fields_number_update - fields_number_original:
            FieldComparator(None, fields_dict_update[fieldNumber]).compare()
        for fieldNumber in fields_number_original & fields_number_update:
            FieldComparator(
                fields_dict_original[fieldNumber],
                fields_dict_update[fieldNumber],
                self.global_resources_original,
                self.global_resources_update,
                self._get_resource_option(self.message_original),
                self._get_resource_option(self.message_update),
            ).compare()

    def _compareNestedMessages(self, nested_msg_dict_original, nested_msg_dict_update):
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

    def _compareResources(
        self,
        message_original,
        message_update,
    ):
        resource_original = self._get_resource_option(message_original)
        resource_update = self._get_resource_option(message_update)
        if not resource_original and not resource_update:
            return
        # 1. A new resource definition is added.
        if not resource_original and resource_update:
            FindingContainer.addFinding(
                FindingCategory.RESOURCE_DEFINITION_ADDITION,
                "",
                f"A message-level resource definition {resource_update.type} has been added.",
                False,
            )
            return
        # 2. Message-level resource definitions removal may not be breaking change since
        # the resource could be moved to file-level resource definition.
        # 3. Note that the type change of an existing resource definition is like one resource
        # is removed and another one is added.
        if (resource_original and not resource_update) or (
            resource_original.type != resource_update.type
        ):
            # Check if the removed resource is in the global file-level resource database.
            if resource_original.type not in self.global_resources_update.types:
                FindingContainer.addFinding(
                    FindingCategory.RESOURCE_DEFINITION_REMOVAL,
                    "",
                    f"A message-level resource definition {resource_original.type} has been removed.",
                    True,
                )
            else:
                # Check the patterns of existing file-level resource are compatible with
                # the patterns of the removed message-level resource.
                global_resource_pattern = self.global_resources_update.types[
                    resource_original.type
                ].pattern

                # If there is pattern removal, or pattern value change. Then the global file-level resource
                # can not replace the original message-level resource.
                if self._compatible_patterns(
                    resource_original.pattern, global_resource_pattern
                ):
                    FindingContainer.addFinding(
                        FindingCategory.RESOURCE_DEFINITION_REMOVAL,
                        "",
                        f"A message-level resource definition {resource_original.type} has been removed.",
                        True,
                    )
            return
        # Resource is existing in both original and update versions.
        # 3. Patterns of message-level resource definitions have changed.
        if self._compatible_patterns(
            resource_original.pattern, resource_update.pattern
        ):
            FindingContainer.addFinding(
                FindingCategory.RESOURCE_DEFINITION_CHANGE,
                "",
                f"The pattern of message-level resource definition has changed from {resource_original.pattern} to {resource_update.pattern}.",
                True,
            )

    def _get_resource_option(self, message):
        resource = message.options.Extensions[resource_pb2.resource]
        if not resource.type or not resource.pattern:
            return None
        return resource

    def _compatible_patterns(self, patterns_original, patterns_update):
        # An existing pattern is removed.
        if len(patterns_original) > len(patterns_update):
            return True
        # An existing pattern value is changed.
        for old_pattern, new_pattern in zip(patterns_original, patterns_update):
            if old_pattern != new_pattern:
                return True
        return False

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

from google.protobuf.descriptor_pb2 import FileDescriptorSet
from src.comparator.service_comparator import ServiceComparator
from src.comparator.message_comparator import DescriptorComparator
from src.comparator.enum_comparator import EnumComparator
from src.comparator.wrappers import FileSet
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class FileSetComparator:
    def __init__(
        self,
        file_set_original: FileSet,
        file_set_update: FileSet,
    ):
        self.fs_original = file_set_original
        self.fs_update = file_set_update

    def compare(self):
        # 1.Compare the per-language packaging options.
        self._compare_packaging_options(self.fs_original, self.fs_update)
        # 2. Check the services map.
        self._compare_services(self.fs_original, self.fs_update)
        # 3. Check the messages map.
        self._compare_messages(self.fs_original, self.fs_update)
        # 4. Check the enums map.
        self._compare_enums(self.fs_original, self.fs_update)
        # 5. Check the file-level resource definitions.
        self._compare_resources(self.fs_original, self.fs_update)

    def _compare_packaging_options(self, fs_original, fs_update):
        packaging_options_original = fs_original.packaging_options_map
        packaging_options_update = fs_update.packaging_options_map
        for option in packaging_options_original.keys():
            language_option_original = set(packaging_options_original[option].keys())
            language_option_update = set(packaging_options_update[option].keys())
            for language_option in language_option_original - language_option_update:
                removed_option = packaging_options_original[option][language_option]
                FindingContainer.addFinding(
                    category=FindingCategory.PACKAGING_OPTION_REMOVAL,
                    proto_file_name=removed_option.proto_file_name,
                    source_code_line=removed_option.source_code_line,
                    message=f"An exisiting packaging option for {option} is removed.",
                    actionable=True,
                )
            for language_option in language_option_update - language_option_original:
                added_option = packaging_options_update[option][language_option]
                FindingContainer.addFinding(
                    category=FindingCategory.PACKAGING_OPTION_ADDITION,
                    proto_file_name=added_option.proto_file_name,
                    source_code_line=added_option.source_code_line,
                    message=f"An exisiting packaging option for {option} is added.",
                    actionable=True,
                )

    def _compare_services(self, fs_original, fs_update):
        keys_original = set(fs_original.services_map.keys())
        keys_update = set(fs_update.services_map.keys())
        for name in keys_original - keys_update:
            ServiceComparator(fs_original.services_map.get(name), None).compare()
        for name in keys_update - keys_original:
            ServiceComparator(None, fs_update.services_map.get(name)).compare()
        for name in keys_update & keys_original:
            ServiceComparator(
                fs_original.services_map.get(name),
                fs_update.services_map.get(name),
            ).compare()

    def _compare_messages(self, fs_original, fs_update):
        keys_original = set(fs_original.messages_map.keys())
        keys_update = set(fs_update.messages_map.keys())
        for name in keys_original - keys_update:
            DescriptorComparator(fs_original.messages_map.get(name), None).compare()
        for name in keys_update - keys_original:
            DescriptorComparator(None, fs_update.messages_map.get(name)).compare()
        for name in keys_update & keys_original:
            DescriptorComparator(
                fs_original.messages_map.get(name),
                fs_update.messages_map.get(name),
            ).compare()

    def _compare_enums(self, fs_original, fs_update):
        keys_original = set(fs_original.enums_map.keys())
        keys_update = set(fs_update.enums_map.keys())
        for name in keys_original - keys_update:
            EnumComparator(fs_original.enums_map.get(name), None).compare()
        for name in keys_update - keys_original:
            EnumComparator(None, fs_update.enums_map.get(name)).compare()
        for name in keys_update & keys_original:
            EnumComparator(
                fs_original.enums_map.get(name), fs_update.enums_map.get(name)
            ).compare()

    def _compare_resources(self, fs_original, fs_update):
        resources_original = fs_original.resources_database
        resources_update = fs_update.resources_database
        resources_types_original = set(resources_original.types.keys())
        resources_types_update = set(resources_update.types.keys())
        # 1. Patterns of file-level resource definitions have changed.
        for resource_type in resources_types_original & resources_types_update:
            patterns_original = resources_original.types[resource_type].value.pattern
            patterns_update = resources_update.types[resource_type].value.pattern
            # An existing pattern is removed.
            if len(patterns_original) > len(patterns_update):
                FindingContainer.addFinding(
                    category=FindingCategory.RESOURCE_DEFINITION_CHANGE,
                    proto_file_name=resources_original.types[
                        resource_type
                    ].proto_file_name,
                    source_code_line=resources_original.types[
                        resource_type
                    ].source_code_line,
                    message=f"An existing pattern value of the resource definition '{resource_type}' is removed.",
                    actionable=True,
                )
            # An existing pattern value is changed.
            # A new pattern value appended to the pattern list is not consider breaking change.
            for old_pattern, new_pattern in zip(patterns_original, patterns_update):
                if old_pattern != new_pattern:
                    FindingContainer.addFinding(
                        category=FindingCategory.RESOURCE_DEFINITION_CHANGE,
                        proto_file_name=resources_update.types[
                            resource_type
                        ].proto_file_name,
                        source_code_line=resources_update.types[
                            resource_type
                        ].source_code_line,
                        message=f"Pattern value of the resource definition '{resource_type}' is updated from '{old_pattern}' to '{new_pattern}'.",
                        actionable=True,
                    )

        # 2. File-level resource definitions addition.
        for resource_type in resources_types_update - resources_types_original:
            FindingContainer.addFinding(
                category=FindingCategory.RESOURCE_DEFINITION_ADDITION,
                proto_file_name=resources_update.types[resource_type].proto_file_name,
                source_code_line=resources_update.types[resource_type].source_code_line,
                message=f"A file-level resource definition '{resource_type}' has been added.",
                actionable=False,
            )
        # 3. File-level resource definitions removal may not be breaking change since
        # the resource could be moved to message-level. This will be checked in the message
        # and field level (where the resource is referenced).

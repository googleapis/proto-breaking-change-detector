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

from src.comparator.service_comparator import ServiceComparator
from src.comparator.message_comparator import DescriptorComparator
from src.comparator.enum_comparator import EnumComparator
from src.comparator.wrappers import FileSet
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory, ChangeType


class FileSetComparator:
    def __init__(
        self,
        file_set_original: FileSet,
        file_set_update: FileSet,
        finding_container: FindingContainer,
    ):
        self.fs_original = file_set_original
        self.fs_update = file_set_update
        self.finding_container = finding_container

    def compare(self):
        # 1.Compare the per-language packaging options.
        self._compare_packaging_options()
        # 2. Check the services map.
        self._compare_services()
        # 3. Check the messages map.
        self._compare_messages()
        # 4. Check the enums map.
        self._compare_enums()
        # 5. Check the file-level resource definitions.
        self._compare_resources()

    def _compare_packaging_options(self):
        packaging_options_original = self.fs_original.packaging_options_map
        packaging_options_update = self.fs_update.packaging_options_map
        if not packaging_options_original and not packaging_options_update:
            return
        for option in packaging_options_original.keys():
            per_language_options_original = set(
                packaging_options_original[option].keys()
            )
            per_language_options_update = set(packaging_options_update[option].keys())
            # Compare the option of `java_outer_classname`.
            # No minor version updates need to consider.
            if option == "java_outer_classname":
                for classname in (
                    per_language_options_original - per_language_options_update
                ):
                    classname_option = packaging_options_original[option][classname]
                    self.finding_container.addFinding(
                        category=FindingCategory.PACKAGING_OPTION_REMOVAL,
                        proto_file_name=classname_option.proto_file_name,
                        source_code_line=classname_option.source_code_line,
                        message=f"An exisiting packaging option `{classname}` for `{option}` is removed.",
                        change_type=ChangeType.MAJOR,
                    )
            # Compare the option of language namespace. Minor version updates in consideration.
            else:
                # Replace the version in the original packaging options with new api version.
                # Transformed map is to store the original option value and replaced option value.
                transformed_option_value_original = {}
                transformed_option_value_update = {}
                for namespace in per_language_options_original:
                    transformed_name = self._get_version_update_name(namespace.lower())
                    transformed_option_value_original[transformed_name] = namespace
                for namespace in per_language_options_update:
                    transformed_option_value_update[namespace.lower()] = namespace

                for namespace in set(transformed_option_value_original.keys()) - set(
                    transformed_option_value_update.keys()
                ):
                    original_option_value = transformed_option_value_original[namespace]
                    namespace_option = packaging_options_original[option][
                        original_option_value
                    ]
                    self.finding_container.addFinding(
                        category=FindingCategory.PACKAGING_OPTION_REMOVAL,
                        proto_file_name=namespace_option.proto_file_name,
                        source_code_line=namespace_option.source_code_line,
                        message=f"An exisiting packaging option `{original_option_value}` for `{option}` is removed.",
                        change_type=ChangeType.MAJOR,
                    )
                for namespace in set(transformed_option_value_update.keys()) - set(
                    transformed_option_value_original.keys()
                ):
                    original_option_value = transformed_option_value_update[namespace]
                    namespace_option = packaging_options_update[option][
                        original_option_value
                    ]
                    self.finding_container.addFinding(
                        category=FindingCategory.PACKAGING_OPTION_ADDITION,
                        proto_file_name=namespace_option.proto_file_name,
                        source_code_line=namespace_option.source_code_line,
                        message=f"A new packaging option `{original_option_value}` for `{option}` is added.",
                        change_type=ChangeType.MAJOR,
                    )

    def _compare_services(self):
        keys_original = set(self.fs_original.services_map.keys())
        keys_update = set(self.fs_update.services_map.keys())
        for name in keys_original - keys_update:
            ServiceComparator(
                self.fs_original.services_map[name], None, self.finding_container
            ).compare()
        for name in keys_update - keys_original:
            ServiceComparator(
                None, self.fs_update.services_map[name], self.finding_container
            ).compare()
        for name in keys_update & keys_original:
            ServiceComparator(
                self.fs_original.services_map[name],
                self.fs_update.services_map[name],
                self.finding_container,
            ).compare()

    def _compare_messages(self):
        keys_original = set(self.fs_original.messages_map.keys())
        keys_update = set(self.fs_update.messages_map.keys())
        compared_update_keys = set()
        for name in keys_original:
            transformed_name = (
                name if name in keys_update else self._get_version_update_name(name)
            )
            if transformed_name in keys_update:
                # Common dependency or same message with version updates.
                DescriptorComparator(
                    self.fs_original.messages_map[name],
                    self.fs_update.messages_map[transformed_name],
                    self.finding_container,
                ).compare()
                compared_update_keys.add(transformed_name)
            else:
                # Message only exits in the original version.
                message = self.fs_original.messages_map[name]
                definition_files = [f.name for f in self.fs_original.definition_files]
                if message.proto_file_name not in definition_files:
                    # The removed message is imported from dependency files.
                    # This should be caught at the fields level where this message is referenced.
                    continue
                DescriptorComparator(
                    self.fs_original.messages_map[name],
                    None,
                    self.finding_container,
                ).compare()
        for name in keys_update - compared_update_keys:
            # Message only exits in the update version.
            message = self.fs_update.messages_map[name]
            definition_files = [f.name for f in self.fs_update.definition_files]
            if message.proto_file_name not in definition_files:
                # The added message is imported from dependency files.
                # This should be caught at the fields level where this message is referenced.
                continue
            DescriptorComparator(
                None,
                self.fs_update.messages_map[name],
                self.finding_container,
            ).compare()

    def _compare_enums(self):
        keys_original = set(self.fs_original.enums_map.keys())
        keys_update = set(self.fs_update.enums_map.keys())
        compared_update_keys = set()
        for name in keys_original:
            transformed_name = (
                name if name in keys_update else self._get_version_update_name(name)
            )
            if transformed_name in keys_update:
                # Common dependency or same enum with version updates.
                EnumComparator(
                    self.fs_original.enums_map[name],
                    self.fs_update.enums_map[transformed_name],
                    self.finding_container,
                ).compare()
                compared_update_keys.add(transformed_name)
            else:
                # Enum only exits in the original version.
                removed_enum = self.fs_original.enums_map[name]
                definition_files = [f.name for f in self.fs_original.definition_files]
                if removed_enum.proto_file_name not in definition_files:
                    # The removed enum is imported from dependency files.
                    # This should be caught at the fields level where this enum is referenced.
                    continue
                EnumComparator(
                    self.fs_original.enums_map[name],
                    None,
                    self.finding_container,
                ).compare()
        for name in keys_update - compared_update_keys:
            # Enum only exits in the update version.
            added_enum = self.fs_update.enums_map[name]
            definition_files = [f.name for f in self.fs_update.definition_files]
            if added_enum.proto_file_name not in definition_files:
                # The added enum is imported from dependency files.
                # This should be caught at the fields level where this enum is referenced.
                continue
            EnumComparator(
                None,
                self.fs_update.enums_map[name],
                self.finding_container,
            ).compare()

    def _compare_resources(self):
        resources_original = self.fs_original.used_resources_database
        resources_update = self.fs_update.used_resources_database
        resources_types_original = set(resources_original.types.keys())
        resources_types_update = set(resources_update.types.keys())
        # 1. Patterns of file-level resource definitions have changed.
        for resource_type in resources_types_original & resources_types_update:
            patterns_original = resources_original.types[resource_type].value.pattern
            patterns_update = resources_update.types[resource_type].value.pattern
            # An existing pattern is removed.
            if len(patterns_original) > len(patterns_update):
                self.finding_container.addFinding(
                    category=FindingCategory.RESOURCE_DEFINITION_CHANGE,
                    proto_file_name=resources_original.types[
                        resource_type
                    ].proto_file_name,
                    source_code_line=resources_original.types[
                        resource_type
                    ].source_code_line,
                    message=f"An existing pattern value of the resource definition `{resource_type}` is removed.",
                    change_type=ChangeType.MAJOR,
                )
            # An existing pattern value is changed.
            # A new pattern value appended to the pattern list is not consider breaking change.
            for old_pattern, new_pattern in zip(patterns_original, patterns_update):
                if old_pattern != new_pattern:
                    self.finding_container.addFinding(
                        category=FindingCategory.RESOURCE_DEFINITION_CHANGE,
                        proto_file_name=resources_update.types[
                            resource_type
                        ].proto_file_name,
                        source_code_line=resources_update.types[
                            resource_type
                        ].source_code_line,
                        message=f"An existing pattern value of the resource definition `{resource_type}` is updated from `{old_pattern}` to `{new_pattern}`.",
                        change_type=ChangeType.MAJOR,
                    )

        # 2. File-level resource definitions addition.
        for resource_type in resources_types_update - resources_types_original:
            self.finding_container.addFinding(
                category=FindingCategory.RESOURCE_DEFINITION_ADDITION,
                proto_file_name=resources_update.types[resource_type].proto_file_name,
                source_code_line=resources_update.types[resource_type].source_code_line,
                message=f"A new resource definition `{resource_type}` has been added.",
                change_type=ChangeType.MINOR,
            )
        # 3. File-level resource definitions removal.
        for resource_type in resources_types_original - resources_types_update:
            self.finding_container.addFinding(
                category=FindingCategory.RESOURCE_DEFINITION_REMOVAL,
                proto_file_name=resources_original.types[resource_type].proto_file_name,
                source_code_line=resources_original.types[
                    resource_type
                ].source_code_line,
                message=f"An existing resource definition `{resource_type}` has been removed.",
                change_type=ChangeType.MAJOR,
            )

    def _get_version_update_name(self, name):
        original_version = self.fs_original.api_version
        update_version = self.fs_update.api_version
        if not original_version or not update_version:
            # No replacement is needed, return the original name.
            return name
        return name.replace(original_version, update_version)

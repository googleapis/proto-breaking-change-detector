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
        if not packaging_options_original and not packaging_options_update:
            return
        api_version_original = fs_original.api_version
        api_version_update = fs_update.api_version
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
                    transformed_option_value_original[
                        namespace.lower().replace(
                            api_version_original, api_version_update
                        )
                    ] = namespace
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
                self.finding_container,
            ).compare()

    def _compare_messages(self, fs_original, fs_update):
        keys_original = set(fs_original.messages_map.keys())
        keys_update = set(fs_update.messages_map.keys())
        for name in keys_original - keys_update:
            DescriptorComparator(
                fs_original.messages_map.get(name),
                None,
                self.finding_container,
            ).compare()
        for name in keys_update - keys_original:
            DescriptorComparator(
                None,
                fs_update.messages_map.get(name),
                self.finding_container,
            ).compare()
        for name in keys_update & keys_original:
            DescriptorComparator(
                fs_original.messages_map.get(name),
                fs_update.messages_map.get(name),
                self.finding_container,
            ).compare()

    def _compare_enums(self, fs_original, fs_update):
        keys_original = set(fs_original.enums_map.keys())
        keys_update = set(fs_update.enums_map.keys())
        for name in keys_original - keys_update:
            EnumComparator(
                fs_original.enums_map.get(name),
                None,
                self.finding_container,
            ).compare()
        for name in keys_update - keys_original:
            EnumComparator(
                None,
                fs_update.enums_map.get(name),
                self.finding_container,
            ).compare()
        for name in keys_update & keys_original:
            EnumComparator(
                fs_original.enums_map.get(name),
                fs_update.enums_map.get(name),
                self.finding_container,
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

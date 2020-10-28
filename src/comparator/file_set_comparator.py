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
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor_pb2 import FileOptions
from google.protobuf.descriptor_pb2 import DescriptorProto
from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.descriptor_pb2 import EnumDescriptorProto
from src.comparator.service_comparator import ServiceComparator
from src.comparator.message_comparator import DescriptorComparator
from src.comparator.enum_comparator import EnumComparator
from src.comparator.resource_database import ResourceDatabase
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory
from typing import Dict, Optional


class _FileSet:
    # TODO(xiaozhenliu): check with One-platform about the version naming.
    # We should allow minor version updates, then the packaging options like
    # `java_package = "com.pubsub.v1"` will always be changed. But versions
    # updates between two stable versions (e.g. v1 to v2) is not permitted.

    def __init__(self, file_set: FileDescriptorSet):
        self.packaging_options_map = {}
        self.services_map: Dict[str, ServiceDescriptorProto] = {}
        self.messages_map: Dict[str, DescriptorProto] = {}
        self.enums_map: Dict[str, EnumDescriptorProto] = {}
        self.resources_database = ResourceDatabase()
        for fd in file_set.file:
            # Create packaging options map and duplicate the per-language rules for namespaces.
            self.packaging_options_map = self._get_packaging_options_map(fd.options)
            self.services_map.update((service.name, service) for service in fd.service)
            self.messages_map.update(
                (message.name, message) for message in fd.message_type
            )
            self.enums_map.update((enum.name, enum) for enum in fd.enum_type)
            for resource in fd.options.Extensions[resource_pb2.resource_definition]:
                self.resources_database.register_resource(resource)

    def _get_packaging_options_map(self, file_options: FileOptions):
        pass


class FileSetComparator:
    def __init__(
        self,
        file_set_original: FileDescriptorSet,
        file_set_update: FileDescriptorSet,
    ):
        self.fs_original = _FileSet(file_set_original)
        self.fs_update = _FileSet(file_set_update)

    def compare(self):
        # 1.TODO(xiaozhenliu) Compare the per-language packaging options.
        # 2. Check the services map.
        self._compare_services(self.fs_original, self.fs_update)
        # 3. Check the messages map.
        self._compare_messages(self.fs_original, self.fs_update)
        # 4. Check the enums map.
        self._compare_enums(self.fs_original, self.fs_update)
        # 5. Check the file-level resource definitions
        self._compare_resources(self.fs_original, self.fs_update)

    def _compare_services(self, fs_original, fs_update):
        keys_original = set(fs_original.services_map.keys())
        keys_update = set(fs_update.services_map.keys())
        for name in keys_original - keys_update:
            ServiceComparator(
                fs_original.services_map.get(name), None, fs_original.messages_map, None
            ).compare()
        for name in keys_update - keys_original:
            ServiceComparator(
                None, fs_update.services_map.get(name), None, fs_update.messages_map
            ).compare()
        for name in keys_update & keys_original:
            ServiceComparator(
                fs_original.services_map.get(name),
                fs_update.services_map.get(name),
                fs_original.messages_map,
                fs_update.messages_map,
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
                fs_original.messages_map.get(name), fs_update.messages_map.get(name)
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
            patterns_original = resources_original.types[resource_type].pattern
            patterns_update = resources_update.types[resource_type].pattern
            # An existing pattern is removed.
            if len(patterns_original) > len(patterns_update):
                FindingContainer.addFinding(
                    FindingCategory.RESOURCE_DEFINITION_CHANGE,
                    "",
                    f"An existing pattern value of the resource definition '{resource_type}' is removed.",
                    True,
                )
            # An existing pattern value is changed.
            # A new pattern value appended to the pattern list is not consider breaking change.
            for old_pattern, new_pattern in zip(patterns_original, patterns_update):
                if old_pattern != new_pattern:
                    FindingContainer.addFinding(
                        FindingCategory.RESOURCE_DEFINITION_CHANGE,
                        "",
                        f"Pattern value of the resource definition '{resource_type}' is updated from '{old_pattern}' to '{new_pattern}'.",
                        True,
                    )

        # 2. File-level resource definitions addition.
        for resource_type in resources_types_update - resources_types_original:
            FindingContainer.addFinding(
                FindingCategory.RESOURCE_DEFINITION_ADDITION,
                "",
                f"A file-level resource definition '{resource_type}' has been added.",
                False,
            )
        # 3. File-level resource definitions removal may not be breaking change since
        # the resource could be moved to message-level. This will be checked in the message
        # and field level (where the resource is referenced).

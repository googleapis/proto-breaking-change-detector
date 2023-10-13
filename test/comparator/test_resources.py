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

import unittest
import os
from proto_bcd.detector.loader import Loader
from proto_bcd.comparator.file_set_comparator import FileSetComparator
from proto_bcd.findings.finding_container import FindingContainer
from proto_bcd.comparator.wrappers import FileSet


class ResourceReferenceTest(unittest.TestCase):
    # This is for tesing the behavior of resources in comparators.
    # The resource can be defined in file-level and message-level.
    # And it is referenced in field-level. So whether the removal of a resource is a breaking change
    # depends on the information from multiple levels (From File or Message to Field).
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.
    PROTO_DIR = os.path.join(os.getcwd(), "test/testdata/protos/example/")
    COMMON_PROTOS_DIR = os.path.join(os.getcwd(), "api-common-protos")

    def setUp(self):
        self.finding_container = FindingContainer()

    def test_resources_change(self):
        _INVOKER_ORIGNAL = Loader(
            proto_definition_dirs=[self.PROTO_DIR, self.COMMON_PROTOS_DIR],
            proto_files=[os.path.join(self.PROTO_DIR, "resource_database_v1.proto")],
            descriptor_set=None,
        )
        _INVOKER_UPDATE = Loader(
            proto_definition_dirs=[self.PROTO_DIR, self.COMMON_PROTOS_DIR],
            proto_files=[
                os.path.join(self.PROTO_DIR, "resource_database_v1beta1.proto")
            ],
            descriptor_set=None,
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.get_descriptor_set()),
            FileSet(_INVOKER_UPDATE.get_descriptor_set()),
            self.finding_container,
        ).compare()

        addition_finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "RESOURCE_PATTERN_ADDITION"
        )
        removal_finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "RESOURCE_PATTERN_REMOVAL"
        )
        resource_definition_removal_finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "RESOURCE_DEFINITION_REMOVAL"
        )
        self.assertEqual(
            addition_finding.location.proto_file_name,
            "resource_database_v1.proto",
        )
        self.assertEqual(addition_finding.location.source_code_line, 13)

        self.assertEqual(
            removal_finding.location.proto_file_name,
            "resource_database_v1.proto",
        )
        self.assertEqual(
            removal_finding.location.source_code_line,
            13,
        )
        self.assertEqual(
            resource_definition_removal_finding.location.proto_file_name,
            "resource_database_v1.proto",
        )
        self.assertEqual(
            resource_definition_removal_finding.location.source_code_line, 34
        )
        self.assertEqual(resource_definition_removal_finding.change_type.value, 1)

    def test_resource_reference_change(self):
        _INVOKER_ORIGNAL = Loader(
            proto_definition_dirs=[self.PROTO_DIR, self.COMMON_PROTOS_DIR],
            proto_files=[os.path.join(self.PROTO_DIR, "resource_reference_v1.proto")],
            descriptor_set=None,
        )
        _INVOKER_UPDATE = Loader(
            proto_definition_dirs=[self.PROTO_DIR, self.COMMON_PROTOS_DIR],
            proto_files=[
                os.path.join(self.PROTO_DIR, "resource_reference_v1beta1.proto")
            ],
            descriptor_set=None,
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.get_descriptor_set()),
            FileSet(_INVOKER_UPDATE.get_descriptor_set()),
            self.finding_container,
        ).compare()
        finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "RESOURCE_REFERENCE_CHANGE_CHILD_TYPE"
        )
        self.assertEqual(
            finding.location.proto_file_name, "resource_reference_v1beta1.proto"
        )
        self.assertEqual(finding.location.source_code_line, 25)
        # Find more details in comments of `resource_reference_v1beta1.proto`
        # 1. Resource_reference annotation is removed for `string name=1`,
        # but it is added in message-level. Non-breaking change.
        # 2. File-level resource definition `t2` is removed, but is added
        # to message-level resource. Non-breaking change.
        breaking_changes = self.finding_container.get_actionable_findings()
        self.assertEqual(len(breaking_changes), 2)
        self.assertEqual(
            breaking_changes[0].category.name, "MESSAGE_MOVED_TO_ANOTHER_FILE"
        )
        self.assertEqual(
            breaking_changes[1].category.name, "RESOURCE_REFERENCE_CHANGE_CHILD_TYPE"
        )


if __name__ == "__main__":
    unittest.main()

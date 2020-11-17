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
from src.detector.loader import Loader
from src.comparator.file_set_comparator import FileSetComparator
from src.findings.finding_container import FindingContainer
from src.comparator.wrappers import FileSet


class ResourceReferenceTest(unittest.TestCase):
    # This is for tesing the behavior of resources in comparators.
    # The resource can be defined in file-level and message-level.
    # And it is referenced in field-level. So whether the removal of a resource is a breaking change
    # depends on the information from multiple levels (From File or Message to Field).
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.
    PROTO_DIR = os.path.join(os.getcwd(), "test/testdata/protos/example/")

    def tearDown(self):
        FindingContainer.reset()

    def test_resources_change(self):
        _INVOKER_ORIGNAL = Loader(
            [self.PROTO_DIR],
            [os.path.join(self.PROTO_DIR, "resource_database_v1.proto")],
        )
        _INVOKER_UPDATE = Loader(
            [self.PROTO_DIR],
            [os.path.join(self.PROTO_DIR, "resource_database_v1beta1.proto")],
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.get_descriptor_set()),
            FileSet(_INVOKER_UPDATE.get_descriptor_set()),
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        # An existing pattern of a file-level resource definition is changed.
        file_resource_pattern_change = findings_map[
            "Pattern value of the resource definition 'example.googleapis.com/t2' is updated from 'foo/{foo}/bar/{bar}/t2' to 'foo/{foo}/bar/{bar}/t2_update'."
        ]
        self.assertEqual(
            file_resource_pattern_change.category.name, "RESOURCE_DEFINITION_CHANGE"
        )
        self.assertEqual(
            file_resource_pattern_change.location.proto_file_name,
            "resource_database_v1beta1.proto",
        )
        self.assertEqual(file_resource_pattern_change.location.source_code_line, 13)
        # A new file-level resource definition is added.
        file_resource_addition = findings_map[
            "A file-level resource definition 'example.googleapis.com/t3' has been added."
        ]
        self.assertEqual(
            file_resource_addition.category.name,
            "RESOURCE_DEFINITION_ADDITION",
        )
        self.assertEqual(
            file_resource_addition.location.proto_file_name,
            "resource_database_v1beta1.proto",
        )
        self.assertEqual(file_resource_addition.location.source_code_line, 19)
        # An existing pattern of a message-level resource annotation is changed.
        message_resource_pattern_change = findings_map[
            "The pattern of an existing message-level resource definition `example.googleapis.com/Foo` has changed from `['foo/{foo}/bar/{bar}']` to `['foo/{foo}/bar']`."
        ]
        self.assertEqual(
            message_resource_pattern_change.category.name,
            "RESOURCE_DEFINITION_CHANGE",
        )
        self.assertEqual(
            message_resource_pattern_change.location.proto_file_name,
            "resource_database_v1beta1.proto",
        )
        self.assertEqual(
            message_resource_pattern_change.location.source_code_line,
            26,
        )
        # An existing message-level resource annotation is removed, and it is not moved to
        # file-level resource definition. So it is a breaking change.
        message_resource_removal = findings_map[
            "An existing message-level resource definition `example.googleapis.com/Test` has been removed."
        ]
        self.assertEqual(
            message_resource_removal.category.name,
            "RESOURCE_DEFINITION_REMOVAL",
        )
        self.assertEqual(
            message_resource_removal.location.proto_file_name,
            "resource_database_v1.proto",
        )
        self.assertEqual(message_resource_removal.location.source_code_line, 34)
        self.assertEqual(message_resource_removal.actionable, True)

    def test_resource_reference_change(self):
        _INVOKER_ORIGNAL = Loader(
            [self.PROTO_DIR],
            [os.path.join(self.PROTO_DIR, "resource_reference_v1.proto")],
        )
        _INVOKER_UPDATE = Loader(
            [self.PROTO_DIR],
            [os.path.join(self.PROTO_DIR, "resource_reference_v1beta1.proto")],
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.get_descriptor_set()),
            FileSet(_INVOKER_UPDATE.get_descriptor_set()),
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        # Type of the resource_reference is changed from type to child_type, but
        # they can not be resoved to the identical resource. Breaking change.
        finding = findings_map[
            "The child_type `example.googleapis.com/t1` and type `example.googleapis.com/t1` of resource reference option in field `topic` cannot be resolved to the identical resource."
        ]
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_CHANGE")
        self.assertEqual(
            finding.location.proto_file_name, "resource_reference_v1beta1.proto"
        )
        self.assertEqual(finding.location.source_code_line, 25)
        # Find more details in comments of `resource_reference_v1beta1.proto`
        # 1. Resource_reference annotation is removed for `string name=1`,
        # but it is added in message-level. Non-breaking change.
        # 2. File-level resource definition `t2` is removed, but is added
        # to message-level resource. Non-breaking change.
        breaking_changes = FindingContainer.getActionableFindings()
        self.assertEqual(len(breaking_changes), 1)


if __name__ == "__main__":
    unittest.main()

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
from test.tools.invoker import UnittestInvoker
from src.comparator.file_set_comparator import FileSetComparator
from src.findings.finding_container import FindingContainer
from src.comparator.wrappers import FileSet


class FileSetComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.service_comparator.ServiceComparator class.
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.

    def tearDown(self):
        FindingContainer.reset()

    def test_service_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["service_v1.proto"], "service_v1_descriptor_set.pb"
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["service_v1beta1.proto"], "service_v1beta1_descriptor_set.pb"
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.run()), FileSet(_INVOKER_UPDATE.run())
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "The paginated response of method paginatedMethod is changed"
        ]
        self.assertEqual(finding.category.name, "METHOD_PAGINATED_RESPONSE_CHANGE")
        self.assertEqual(finding.location.path, "service_v1beta1.proto Line: 11")

        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()

    def test_message_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["message_v1.proto"], "message_v1_descriptor_set.pb"
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["message_v1beta1.proto"], "message_v1beta1_descriptor_set.pb"
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.run()), FileSet(_INVOKER_UPDATE.run())
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map[
                "Type of the field is changed, the original is TYPE_INT32, but the updated is TYPE_STRING"
            ].category.name,
            "FIELD_TYPE_CHANGE",
        )
        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()

    def test_enum_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["enum_v1.proto"], "enum_v1_descriptor_set.pb"
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["enum_v1beta1.proto"], "enum_v1beta1_descriptor_set.pb"
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.run()), FileSet(_INVOKER_UPDATE.run())
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map["An Enum BookType is removed"]
        self.assertEqual(finding.category.name, "ENUM_REMOVAL")
        self.assertEqual(finding.location.path, "enum_v1.proto Line: 5")
        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()

    def test_resources_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["resource_database_v1.proto"],
            "resource_database_v1_descriptor_set.pb",
            True,
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["resource_database_v1beta1.proto"],
            "resource_database_v1beta1_descriptor_set.pb",
            True,
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.run()), FileSet(_INVOKER_UPDATE.run())
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map[
                "Pattern value of the resource definition 'example.googleapis.com/t2' is updated from 'foo/{foo}/bar/{bar}/t2' to 'foo/{foo}/bar/{bar}/t2_update'."
            ].category.name,
            "RESOURCE_DEFINITION_CHANGE",
        )
        self.assertEqual(
            findings_map[
                "A file-level resource definition 'example.googleapis.com/t3' has been added."
            ].category.name,
            "RESOURCE_DEFINITION_ADDITION",
        )
        self.assertEqual(
            findings_map[
                "The pattern of message-level resource definition has changed from ['foo/{foo}/bar/{bar}'] to ['foo/{foo}/bar']."
            ].category.name,
            "RESOURCE_DEFINITION_CHANGE",
        )
        self.assertEqual(
            findings_map[
                "A message-level resource definition example.googleapis.com/Test has been removed."
            ].category.name,
            "RESOURCE_DEFINITION_REMOVAL",
        )
        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()

    def test_resource_reference_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["resource_reference_v1.proto"],
            "resource_reference_v1_descriptor_set.pb",
            True,
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["resource_reference_v1beta1.proto"],
            "resource_reference_v1beta1_descriptor_set.pb",
            True,
        )
        FileSetComparator(
            FileSet(_INVOKER_ORIGNAL.run()), FileSet(_INVOKER_UPDATE.run())
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map[
                "The child_type 'example.googleapis.com/t1' and type 'example.googleapis.com/t1' of resource reference option in field 'topic' cannot be resolved to the identical resource."
            ].category.name,
            "RESOURCE_REFERENCE_CHANGE",
        )
        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

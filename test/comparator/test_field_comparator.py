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
from src.comparator.field_comparator import FieldComparator
from src.comparator.wrappers import FileSet
from src.findings.finding_container import FindingContainer


class FieldComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.field_comparator.FieldComparator class.
    # We use message_v1.proto and message_v1beta1.proto to mimic the original and next
    # versions of the API definition files (which has only one proto file in this case).
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.
    _PROTO_ORIGINAL = "message_v1.proto"
    _PROTO_UPDATE = "message_v1beta1.proto"
    _DESCRIPTOR_SET_ORIGINAL = "message_v1_descriptor_set.pb"
    _DESCRIPTOR_SET_UPDATE = "message_v1beta1_descriptor_set.pb"
    _INVOKER_ORIGNAL = UnittestInvoker([_PROTO_ORIGINAL], _DESCRIPTOR_SET_ORIGINAL)
    _INVOKER_UPDATE = UnittestInvoker([_PROTO_UPDATE], _DESCRIPTOR_SET_UPDATE)
    _PB_ORIGNAL = _INVOKER_ORIGNAL.run()
    _PB_UPDATE = _INVOKER_UPDATE.run()

    def setUp(self):
        self.person_fields_v1 = FileSet(self._PB_ORIGNAL).messages_map["Person"].fields
        self.person_fields_v1beta1 = (
            FileSet(self._PB_UPDATE).messages_map["Person"].fields
        )

    def tearDown(self):
        FindingContainer.reset()

    def test_field_removal(self):
        FieldComparator(self.person_fields_v1[1], None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A Field name is removed")
        self.assertEqual(finding.category.name, "FIELD_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "message_v1.proto")
        self.assertEqual(finding.location.source_code_line, 6)

    def test_field_addition(self):
        FieldComparator(None, self.person_fields_v1[1]).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new Field name is added.")
        self.assertEqual(finding.category.name, "FIELD_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "message_v1.proto")
        self.assertEqual(finding.location.source_code_line, 6)

    def test_type_change(self):
        # Field `id` is `int32` type in `message_v1.proto`,
        # but updated to `string` in `message_v1beta1.proto`.
        FieldComparator(
            self.person_fields_v1[2], self.person_fields_v1beta1[2]
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of the field is changed, the original is TYPE_INT32,"
            " but the updated is TYPE_STRING",
        )
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "message_v1beta1.proto")
        self.assertEqual(finding.location.source_code_line, 7)

    def test_repeated_label_change(self):
        # Field `phones` in `message_v1.proto` has `repeated` label,
        # but it's removed in the `message_v1beta1.proto`.
        FieldComparator(
            self.person_fields_v1[4], self.person_fields_v1beta1[4]
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Repeated state of the Field is changed, the original is LABEL_REPEATED,"
            " but the updated is LABEL_OPTIONAL",
        )
        self.assertEqual(finding.category.name, "FIELD_REPEATED_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "message_v1beta1.proto")
        self.assertEqual(finding.location.source_code_line, 21)

    def test_name_change(self):
        # Field `email = 3` in `message_v1.proto` is renamed to
        # `email_address = 3` in the `message_v1beta1.proto`.
        FieldComparator(
            self.person_fields_v1[3], self.person_fields_v1beta1[3]
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Name of the Field is changed, the original is email, but the updated is email_address",
        )
        self.assertEqual(finding.category.name, "FIELD_NAME_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "message_v1beta1.proto")
        self.assertEqual(finding.location.source_code_line, 8)

    def test_oneof_change(self):
        # Field `single = 5` in `message_v1.proto` is moved out of One-of.
        FieldComparator(
            self.person_fields_v1[5], self.person_fields_v1beta1[5]
        ).compare()
        findings = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings["The existing field single is moved out of One-of."]
        self.assertEqual(finding.category.name, "FIELD_ONEOF_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "message_v1beta1.proto")
        self.assertEqual(finding.location.source_code_line, 22)

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

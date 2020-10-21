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

    def tearDown(self):
        FindingContainer.reset()

    def test_field_removal(self):
        name_field = self._PB_ORIGNAL.file[0].message_type[0].field[0]
        FieldComparator(name_field, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A Field name is removed")
        self.assertEqual(finding.category.name, "FIELD_REMOVAL")

    def test_field_addition(self):
        name_field = self._PB_ORIGNAL.file[0].message_type[0].field[0]
        FieldComparator(None, name_field).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new Field name is added.")
        self.assertEqual(finding.category.name, "FIELD_ADDITION")

    def test_type_change(self):
        # Field `id` is `int32` type in `message_v1.proto`,
        # but updated to `string` in `message_v1beta1.proto`.
        field_id_original = self._PB_ORIGNAL.file[0].message_type[0].field[1]
        field_id_update = self._PB_UPDATE.file[0].message_type[0].field[1]
        FieldComparator(field_id_original, field_id_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of the field is changed, the original is TYPE_INT32,"
            " but the updated is TYPE_STRING",
        )
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")

    def test_repeated_label_change(self):
        # Field `phones` in `message_v1.proto` has `repeated` label,
        # but it's removed in the `message_v1beta1.proto`.
        field_phones_original = self._PB_ORIGNAL.file[0].message_type[0].field[3]
        field_phones_update = self._PB_UPDATE.file[0].message_type[0].field[3]
        FieldComparator(field_phones_original, field_phones_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Repeated state of the Field is changed, the original is LABEL_REPEATED,"
            " but the updated is LABEL_OPTIONAL",
        )
        self.assertEqual(finding.category.name, "FIELD_REPEATED_CHANGE")

    def test_name_change(self):
        # Field `email = 3` in `message_v1.proto` is renamed to
        # `email_address = 3` in the `message_v1beta1.proto`.
        field_email_original = self._PB_ORIGNAL.file[0].message_type[0].field[2]
        field_email_update = self._PB_UPDATE.file[0].message_type[0].field[2]
        FieldComparator(field_email_original, field_email_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Name of the Field is changed, the original is email, but the updated is email_address",
        )
        self.assertEqual(finding.category.name, "FIELD_NAME_CHANGE")

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

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
from test.tools.mock_descriptors import make_field
from src.comparator.field_comparator import FieldComparator
from src.findings.finding_container import FindingContainer


class FieldComparatorTest(unittest.TestCase):
    def tearDown(self):
        FindingContainer.reset()

    def test_field_removal(self):
        self.field_foo = make_field("Foo")
        FieldComparator(self.field_foo, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A Field Foo is removed")
        self.assertEqual(finding.category.name, "FIELD_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_field_addition(self):
        self.field_foo = make_field("Foo")
        FieldComparator(None, self.field_foo).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new Field Foo is added.")
        self.assertEqual(finding.category.name, "FIELD_ADDITION")

    def test_primitive_type_change(self):
        self.field_int = make_field(proto_type="TYPE_INT32")
        self.field_string = make_field(proto_type="TYPE_STRING")
        FieldComparator(self.field_int, self.field_string).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of the field is changed, the original is TYPE_INT32,"
            " but the updated is TYPE_STRING",
        )
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")

    def test_message_type_change(self):
        self.field_message = make_field(type_name=".example.v1.Enum")
        self.field_message_update = make_field(type_name=".example.v1beta1.EnumUpdate")
        FieldComparator(self.field_message, self.field_message_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of the field is changed, the original is `.example.v1.Enum`, but the updated is `.example.v1beta1.EnumUpdate`",
        )
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")

    def test_repeated_label_change(self):
        self.field_repeated = make_field(repeated=True)
        self.field_non_repeated = make_field(repeated=False)
        FieldComparator(self.field_repeated, self.field_non_repeated).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Repeated state of the Field is changed, the original is LABEL_REPEATED,"
            " but the updated is LABEL_OPTIONAL",
        )
        self.assertEqual(finding.category.name, "FIELD_REPEATED_CHANGE")

    def test_name_change(self):
        self.field_foo = make_field("Foo")
        self.field_bar = make_field("Bar")
        FieldComparator(self.field_foo, self.field_bar).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Name of the Field is changed, the original is Foo, but the updated is Bar",
        )
        self.assertEqual(finding.category.name, "FIELD_NAME_CHANGE")

    def test_oneof_change(self):
        self.field_oneof = make_field(name="Foo", oneof=True)
        self.field_not_oneof = make_field(name="Foo")
        FieldComparator(self.field_oneof, self.field_not_oneof).compare()
        findings = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings["The existing field Foo is moved out of One-of."]
        self.assertEqual(finding.category.name, "FIELD_ONEOF_REMOVAL")


if __name__ == "__main__":
    unittest.main()

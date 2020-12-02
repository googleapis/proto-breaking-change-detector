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
from test.tools.mock_descriptors import make_message, make_field, make_enum
from src.comparator.message_comparator import DescriptorComparator
from src.findings.finding_container import FindingContainer
from google.protobuf import descriptor_pb2
from google.api import resource_pb2


class DescriptorComparatorTest(unittest.TestCase):
    def setUp(self):
        self.message_foo = make_message("Message")
        self.finding_container = FindingContainer()

    def test_message_removal(self):
        DescriptorComparator(self.message_foo, None, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "An existing message `Message` is removed.")
        self.assertEqual(finding.category.name, "MESSAGE_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_message_addition(self):
        DescriptorComparator(None, self.message_foo, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "A new message `Message` is added.")
        self.assertEqual(finding.category.name, "MESSAGE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_field_change(self):
        field_int = make_field(proto_type="TYPE_INT32")
        field_string = make_field(proto_type="TYPE_STRING")
        message1 = make_message(fields=[field_int])
        message2 = make_message(fields=[field_string])
        DescriptorComparator(message1, message2, self.finding_container).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map[
            "Type of an existing field `my_field` is changed from `TYPE_INT32` to `TYPE_STRING`."
        ]
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_message_change(self):
        nested_field = make_field(name="nested_field")
        nested_message_with_fields = make_message(
            name="nested_message", fields=[nested_field]
        )
        nested_message_without_fields = make_message(name="nested_message")
        message1 = make_message(nested_messages=[nested_message_with_fields])
        message2 = make_message(nested_messages=[nested_message_without_fields])
        DescriptorComparator(message1, message2, self.finding_container).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map["An existing field `nested_field` is removed."]
        self.assertEqual(finding.category.name, "FIELD_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_enum_change(self):
        nested_enum1 = make_enum(
            name="Foo",
            values=(
                ("RED", 1),
                ("GREEN", 2),
            ),
        )
        nested_enum2 = make_enum(
            name="Foo",
            values=(
                ("RED", 1),
                ("GREEN", 2),
                ("BLUE", 3),
            ),
        )
        message1 = make_message(nested_enums=[nested_enum1])
        message2 = make_message(nested_enums=[nested_enum2])
        DescriptorComparator(message1, message2, self.finding_container).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map["A new EnumValue `BLUE` is added."]
        self.assertEqual(finding.category.name, "ENUM_VALUE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_compatible_patterns(self):
        message_comparator = DescriptorComparator(None, None, None)
        # An existing pattern is removed.
        self.assertFalse(message_comparator._compatible_patterns(["a", "b"], ["a"]))
        # An existing pattern value is changed.
        self.assertFalse(
            message_comparator._compatible_patterns(["a", "b"], ["b", "a"])
        )
        self.assertFalse(message_comparator._compatible_patterns(["a", "b"], ["c"]))
        # An new pattern value is appended.
        self.assertTrue(
            message_comparator._compatible_patterns(["a", "b"], ["a", "b", "c"])
        )
        # Identical patterns
        self.assertTrue(message_comparator._compatible_patterns(["a", "b"], ["a", "b"]))

    def test_compatible_patterns(self):
        message_comparator = DescriptorComparator(None, None, None)
        # An existing pattern is removed.
        self.assertFalse(message_comparator._compatible_patterns(["a", "b"], ["a"]))
        # An existing pattern value is changed.
        self.assertFalse(
            message_comparator._compatible_patterns(["a", "b"], ["b", "a"])
        )
        self.assertFalse(message_comparator._compatible_patterns(["a", "b"], ["c"]))
        # An new pattern value is appended.
        self.assertTrue(
            message_comparator._compatible_patterns(["a", "b"], ["a", "b", "c"])
        )
        # Identical patterns
        self.assertTrue(message_comparator._compatible_patterns(["a", "b"], ["a", "b"]))


if __name__ == "__main__":
    unittest.main()

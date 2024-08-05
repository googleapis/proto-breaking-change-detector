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
from proto_bcd.comparator.message_comparator import DescriptorComparator
from proto_bcd.findings.finding_container import FindingContainer
from google.protobuf import descriptor_pb2
from google.api import resource_pb2


class DescriptorComparatorTest(unittest.TestCase):
    def setUp(self):
        self.message_foo = make_message("Message")
        self.finding_container = FindingContainer()

    def test_message_removal(self):
        DescriptorComparator(
            self.message_foo, None, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "MESSAGE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_message_addition(self):
        DescriptorComparator(
            None, self.message_foo, self.finding_container, context="ctx"
        ).compare()
        findings = self.finding_container.get_all_findings()
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.category.name, "MESSAGE_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_field_type_change(self):
        field_int = make_field(proto_type="TYPE_INT32")
        field_string = make_field(proto_type="TYPE_STRING")
        message1 = make_message(fields=[field_int])
        message2 = make_message(fields=[field_string])
        DescriptorComparator(
            message1, message2, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "FIELD_TYPE_CHANGE"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_field_addition(self):
        field_int = make_field(proto_type="TYPE_INT32")
        message_update = make_message(fields=[field_int])
        DescriptorComparator(
            make_message(), message_update, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "FIELD_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_message_removal(self):
        DescriptorComparator(
            make_message(nested_messages=[make_message(name="nested_message")]),
            make_message(),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "MESSAGE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_message_addition(self):
        DescriptorComparator(
            make_message(),
            make_message(nested_messages=[make_message(name="nested_message")]),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "MESSAGE_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_enum_addition(self):
        DescriptorComparator(
            make_message(),
            make_message(nested_enums=[make_enum(name="nested_message")]),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "ENUM_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_enum_removal(self):
        DescriptorComparator(
            make_message(nested_enums=[make_enum(name="nested_message")]),
            make_message(),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "ENUM_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_nested_message_change(self):
        nested_field = make_field(name="nested_field")
        nested_message_with_fields = make_message(
            name="nested_message", fields=[nested_field]
        )
        nested_message_without_fields = make_message(name="nested_message")
        message1 = make_message(nested_messages=[nested_message_with_fields])
        message2 = make_message(nested_messages=[nested_message_without_fields])
        DescriptorComparator(
            message1, message2, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "FIELD_REMOVAL"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
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
        DescriptorComparator(
            message1, message2, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.get_all_findings()
            if f.category.name == "ENUM_VALUE_ADDITION"
        )
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")


if __name__ == "__main__":
    unittest.main()

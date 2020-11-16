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

    def tearDown(self):
        FindingContainer.reset()

    def test_message_removal(self):
        DescriptorComparator(self.message_foo, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A message Message is removed")
        self.assertEqual(finding.category.name, "MESSAGE_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_message_addition(self):
        DescriptorComparator(None, self.message_foo).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new message Message is added.")
        self.assertEqual(finding.category.name, "MESSAGE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_field_change(self):
        field_int = make_field(proto_type="TYPE_INT32")
        field_string = make_field(proto_type="TYPE_STRING")
        message1 = make_message(fields=[field_int])
        message2 = make_message(fields=[field_string])
        DescriptorComparator(message1, message2).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
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
        DescriptorComparator(message1, message2).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
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
        DescriptorComparator(message1, message2).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map["A new EnumValue BLUE is added."]
        self.assertEqual(finding.category.name, "ENUM_VALUE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_resource_annotation_removal(self):
        # Message-level resource options.
        message_options = descriptor_pb2.MessageOptions()
        resource = message_options.Extensions[resource_pb2.resource]
        resource.pattern.append("foo/{foo}/bar")
        resource.type = "example/Bar"

        # The resource annotation is removed.
        message = make_message("Message", options=message_options)
        message_without_resource = make_message("Message")
        DescriptorComparator(message, message_without_resource).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "A message-level resource definition example/Bar has been removed."
        ]
        self.assertEqual(finding.category.name, "RESOURCE_DEFINITION_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_resource_annotation_addition(self):
        options = descriptor_pb2.MessageOptions()
        resource = options.Extensions[resource_pb2.resource]
        resource.pattern.append("foo/{foo}/bar")
        resource.type = "example/Bar"
        message = make_message("Message", options=options)
        message_without_resource = make_message("Message")
        DescriptorComparator(message_without_resource, message).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "A message-level resource definition example/Bar has been added."
        ]
        self.assertEqual(finding.category.name, "RESOURCE_DEFINITION_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_resource_pattern_change(self):
        # Message-level resource options.
        message_options = descriptor_pb2.MessageOptions()
        resource = message_options.Extensions[resource_pb2.resource]
        resource.pattern.append("foo/{foo}/bar")
        resource.type = "example/Bar"

        message_options_change = descriptor_pb2.MessageOptions()
        resource_two_patterns = message_options_change.Extensions[resource_pb2.resource]
        resource_two_patterns.pattern.append(
            "foo/{foo}/bar",
        )
        resource_two_patterns.pattern.append(
            "foo/{foo}/bar/{bar}",
        )
        resource_two_patterns.type = "example/Bar"
        # The resource annotation is removed.
        message = make_message("Message", options=message_options_change)
        message_pattern_removal = make_message("Message", options=message_options)
        DescriptorComparator(message, message_pattern_removal).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "The pattern of message-level resource definition has changed from ['foo/{foo}/bar', 'foo/{foo}/bar/{bar}'] to ['foo/{foo}/bar']."
        ]
        self.assertEqual(finding.category.name, "RESOURCE_DEFINITION_CHANGE")


if __name__ == "__main__":
    unittest.main()

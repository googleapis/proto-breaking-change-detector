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
from test.tools.mock_descriptors import make_enum_value
from google.protobuf import descriptor_pb2
from src.comparator.enum_value_comparator import EnumValueComparator
from src.findings.finding_container import FindingContainer


class EnumValueComparatorTest(unittest.TestCase):
    def setUp(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        locations = [L(path=(2, 1), span=(1, 2))]
        self.enum_foo = make_enum_value(
            name="FOO",
            number=1,
            proto_file_name="test.proto",
            locations=locations,
            path=(2, 1),
        )
        self.enum_bar = make_enum_value(
            name="BAR",
            number=1,
            proto_file_name="test_update.proto",
            locations=locations,
            path=(2, 1),
        )
        self.finding_container = FindingContainer()

    def test_enum_value_removal(self):
        EnumValueComparator(
            self.enum_foo,
            None,
            self.finding_container,
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "An existing EnumValue `FOO` is removed.")
        self.assertEqual(finding.category.name, "ENUM_VALUE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "test.proto")
        self.assertEqual(finding.location.source_code_line, 2)

    def test_enum_value_addition(self):
        EnumValueComparator(None, self.enum_foo, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "A new EnumValue `FOO` is added.")
        self.assertEqual(finding.category.name, "ENUM_VALUE_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "test.proto")
        self.assertEqual(finding.location.source_code_line, 2)

    def test_name_change(self):
        EnumValueComparator(
            self.enum_foo, self.enum_bar, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message, "Name of the EnumValue is changed from `FOO` to `BAR`."
        )
        self.assertEqual(finding.category.name, "ENUM_VALUE_NAME_CHANGE")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "test_update.proto")
        self.assertEqual(finding.location.source_code_line, 2)

    def test_no_api_change(self):
        EnumValueComparator(
            self.enum_foo, self.enum_foo, self.finding_container
        ).compare()
        self.assertEqual(len(self.finding_container.getAllFindings()), 0)


if __name__ == "__main__":
    unittest.main()

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
from test.tools.mock_descriptors import make_enum
from src.comparator.enum_comparator import EnumComparator
from src.findings.finding_container import FindingContainer
from google.protobuf import descriptor_pb2


class EnumComparatorTest(unittest.TestCase):
    def setUp(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        # fmt: off
        locations = [
            L(path=(4, 0,), span=(1, 2, 3, 4)),
            # Enum will add (2, 1) for each EnumValue in the path.
            L(path=(4, 0, 2, 1), span=(2, 3, 4, 5)),
        ]
        self.enum_foo = make_enum(
            name="Foo",
            values=(
                ("VALUE1", 1),
            ),
            proto_file_name="test.proto",
            locations=locations,
            path=(4, 0,),
        )
        self.enum_bar = make_enum(
            name="Bar",
            values=(
                ("VALUE1", 1),
                ("VALUE2", 2),
            ),
            proto_file_name="test_update.proto",
            locations=locations,
            path=(4, 0,),
        )
        self.finding_container = FindingContainer()
        # fmt: on

    def test_enum_removal(self):
        EnumComparator(
            self.enum_foo, None, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "ENUM_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "test.proto")
        self.assertEqual(finding.location.source_code_line, 2)

    def test_enum_addition(self):
        EnumComparator(
            None, self.enum_bar, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "ENUM_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "test_update.proto")
        self.assertEqual(finding.location.source_code_line, 2)

    def test_enum_value_change(self):
        EnumComparator(
            self.enum_foo, self.enum_bar, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.get_all_findings()[0]
        self.assertEqual(finding.category.name, "ENUM_VALUE_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "test_update.proto")
        self.assertEqual(finding.location.source_code_line, 3)

    def test_no_api_change(self):
        EnumComparator(
            self.enum_foo, self.enum_foo, self.finding_container, context="ctx"
        ).compare()
        self.assertEqual(len(self.finding_container.get_all_findings()), 0)


if __name__ == "__main__":
    unittest.main()

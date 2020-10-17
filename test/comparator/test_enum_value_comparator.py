# Copyright 2019 Google LLC
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
from src.comparator.enum_value_comparator import EnumValueComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class EnumValueComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.enum_valeu_comparator.EnumValueComparator
    # class. We take the two enum values (`MOBILE` and `HOME` in `PhoneType`)
    # in address_book.proto as input to exercise different cases of enum values changes.
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in proto, and
    # create a FileDescriptorSet (_PB_ORIGNAL) out of it.
    _PROTO_ORIGINAL = "address_book.proto"
    _DESCRIPTOR_SET_ORIGINAL = "address_book_descriptor_set.pb"
    _INVOKER_ORIGNAL = UnittestInvoker([_PROTO_ORIGINAL], _DESCRIPTOR_SET_ORIGINAL)
    _PB_ORIGNAL = _INVOKER_ORIGNAL.run()

    def setUp(self):
        # Get `MOBILE` and `HOME` enumValueDescriptorProto from `address_book_descriptor_set.pb`.
        enum_type_values = self._PB_ORIGNAL.file[0].message_type[0].enum_type[0].value
        self.enumValue_mobile = enum_type_values[0]
        self.enumValue_home = enum_type_values[1]

    def tearDown(self):
        FindingContainer.reset()

    def test_enum_value_removal(self):
        EnumValueComparator(self.enumValue_mobile, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "An EnumValue MOBILE is removed")
        self.assertEqual(finding.category.name, "ENUM_VALUE_REMOVAL")

    def test_enum_value_addition(self):
        EnumValueComparator(None, self.enumValue_home).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new EnumValue HOME is added.")
        self.assertEqual(finding.category.name, "ENUM_VALUE_ADDITION")

    def test_name_change(self):
        EnumValueComparator(self.enumValue_mobile, self.enumValue_home).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Name of the EnumValue is changed, the original is MOBILE, but the updated is HOME",
        )
        self.assertEqual(finding.category.name, "ENUM_VALUE_NAME_CHANGE")

    def test_no_api_change(self):
        EnumValueComparator(self.enumValue_mobile, self.enumValue_mobile).compare()
        self.assertEqual(len(FindingContainer.getAllFindings()), 0)

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()


if __name__ == "__main__":
    unittest.main()

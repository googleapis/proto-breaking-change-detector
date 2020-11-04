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
from src.comparator.enum_comparator import EnumComparator
from src.findings.finding_container import FindingContainer
from src.comparator.wrappers import FileSet


class EnumComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.enum_comparator.EnumComparator class.
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
        # We take the enumDescriptorProto `phoneType` and `phoneType` from the original
        # and updated `_descriptor_set.pb` files for comparison.
        self.enum_original = (
            FileSet(self._PB_ORIGNAL).messages_map["Person"].nested_enums["PhoneType"]
        )
        self.enum_update = (
            FileSet(self._PB_UPDATE).messages_map["Person"].nested_enums["PhoneType"]
        )

    def tearDown(self):
        FindingContainer.reset()

    def test_enum_removal(self):
        EnumComparator(self.enum_original, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "An Enum PhoneType is removed")
        self.assertEqual(finding.category.name, "ENUM_REMOVAL")
        self.assertEqual(finding.location.path, "message_v1.proto Line: 10")

    def test_enum_addition(self):
        EnumComparator(None, self.enum_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new Enum PhoneType is added.")
        self.assertEqual(finding.category.name, "ENUM_ADDITION")
        self.assertEqual(finding.location.path, "message_v1beta1.proto Line: 10")

    def test_enum_value_change(self):
        EnumComparator(self.enum_original, self.enum_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new EnumValue SCHOOL is added.")
        self.assertEqual(finding.category.name, "ENUM_VALUE_ADDITION")

    def test_no_api_change(self):
        EnumComparator(self.enum_update, self.enum_update).compare()
        self.assertEqual(len(FindingContainer.getAllFindings()), 0)

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

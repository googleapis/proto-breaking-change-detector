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
from src.findings.finding_container import FindingContainer
from src.findings.finding_category import FindingCategory, ChangeType


class FindingContainerTest(unittest.TestCase):
    # The unit tests are executed in alphabetical order by test name
    # automatically, so test_reset() will be run in the middle which will break us.
    # This is a monolithic test, so we give numbers to indicate
    # the steps and also ensure the execution orders.
    finding_container = FindingContainer()

    def test1_add_findings(self):
        self.finding_container.addFinding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="my_proto.proto",
            source_code_line=12,
            change_type=ChangeType.MAJOR,
            subject="subject",
            context="context",
        )
        self.assertEqual(len(self.finding_container.getAllFindings()), 1)

    def test2_get_actionable_findings(self):
        self.finding_container.addFinding(
            category=FindingCategory.FIELD_ADDITION,
            proto_file_name="my_proto.proto",
            source_code_line=15,
            change_type=ChangeType.MINOR,
        )
        self.assertEqual(len(self.finding_container.getActionableFindings()), 1)

    def test3_toDictArr(self):
        dict_arr_output = self.finding_container.toDictArr()
        self.assertEqual(dict_arr_output[0]["category"], "METHOD_REMOVAL")
        self.assertEqual(dict_arr_output[1]["category"], "FIELD_ADDITION")

    def test4_toHumanReadableMessage(self):
        self.finding_container.addFinding(
            category=FindingCategory.RESOURCE_DEFINITION_REMOVAL,
            proto_file_name="my_proto.proto",
            source_code_line=5,
            change_type=ChangeType.MAJOR,
            subject="subject",
        )
        self.finding_container.addFinding(
            category=FindingCategory.METHOD_SIGNATURE_REMOVAL,
            proto_file_name="my_other_proto.proto",
            source_code_line=-1,
            change_type=ChangeType.MAJOR,
            type="type",
            subject="subject",
            context="context",
        )
        self.assertEqual(
            self.finding_container.toHumanReadableMessage(),
            "my_other_proto.proto: An existing method_signature `type` is removed from method `subject` in service `context`.\n"
            + "my_proto.proto L5: An existing resource_definition `subject` is removed.\n"
            + "my_proto.proto L12: An existing method `subject` is removed from service `context`.\n",
        )


if __name__ == "__main__":
    unittest.main()

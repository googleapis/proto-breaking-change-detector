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
import json
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class FindingContainerTest(unittest.TestCase):
    # The unit tests are executed in alphabetical order by test name
    # automatically, so test_reset() will be run in the middle which will break us.
    # This is a monolithic test, so we give numbers to indicate
    # the steps and also ensure the execution orders.
    def test1_add_findings(self):
        FindingContainer.addFinding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="my_proto.proto",
            source_code_line=12,
            message="An rpc method bar is removed.",
            actionable=True,
        )
        self.assertEqual(len(FindingContainer.getAllFindings()), 1)

    def test2_get_actionable_findings(self):
        FindingContainer.addFinding(
            category=FindingCategory.FIELD_ADDITION,
            proto_file_name="my_proto.proto",
            source_code_line=15,
            message="Not breaking change.",
            actionable=False,
        )
        self.assertEqual(len(FindingContainer.getActionableFindings()), 1)

    def test3_toJson(self):
        json_output = FindingContainer.toJson()
        items = json.loads(json_output)
        self.assertEqual(items[0]["category"], "METHOD_REMOVAL")
        self.assertEqual(items[1]["category"], "FIELD_ADDITION")

    def test4_toHumanReadableMessage(self):
        FindingContainer.addFinding(
            category=FindingCategory.RESOURCE_DEFINITION_CHANGE,
            proto_file_name="my_proto.proto",
            source_code_line=5,
            message="An existing file-level resource definition has changed.",
            actionable=True,
        )
        self.assertEqual(
            FindingContainer.toHumanReadableMessage(),
            "my_proto.proto L5: An existing file-level resource definition has changed.\n"
            + "my_proto.proto L12: An rpc method bar is removed.\n",
        )

    def test5_reset(self):
        FindingContainer.reset()
        self.assertEqual(len(FindingContainer.getAllFindings()), 0)


if __name__ == "__main__":
    unittest.main()

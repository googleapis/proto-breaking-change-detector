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
from proto_bcd.findings.finding_container import FindingContainer
from proto_bcd.findings.finding_category import (
    FindingCategory,
    ChangeType,
    ConventionalCommitTag,
)


class FindingContainerTest(unittest.TestCase):
    # The unit tests are executed in alphabetical order by test name
    # automatically, so test_reset() will be run in the middle which will break us.
    # This is a monolithic test, so we give numbers to indicate
    # the steps and also ensure the execution orders.
    finding_container = FindingContainer()

    def test1_add_findings(self):
        self.finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="my_proto.proto",
            source_code_line=12,
            conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
            subject="subject",
            context="context",
        )
        self.assertEqual(len(self.finding_container.get_all_findings()), 1)

    def test2_get_actionable_findings(self):
        self.finding_container.add_finding(
            category=FindingCategory.FIELD_ADDITION,
            proto_file_name="my_proto.proto",
            source_code_line=15,
            conventional_commit_tag=ConventionalCommitTag.FEAT,
        )
        self.assertEqual(len(self.finding_container.get_actionable_findings()), 1)

    def test3_to_dict_arr(self):
        dict_arr_output = self.finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["category"], "METHOD_REMOVAL")
        self.assertEqual(dict_arr_output[1]["category"], "FIELD_ADDITION")

    def test4_to_human_readable_message(self):
        self.finding_container.add_finding(
            category=FindingCategory.RESOURCE_DEFINITION_REMOVAL,
            proto_file_name="my_proto.proto",
            source_code_line=5,
            conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
            subject="subject",
        )
        self.finding_container.add_finding(
            category=FindingCategory.METHOD_SIGNATURE_REMOVAL,
            proto_file_name="my_other_proto.proto",
            source_code_line=-1,
            conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
            type="type",
            subject="subject",
            context="context",
        )
        self.assertEqual(
            self.finding_container.to_human_readable_message(),
            "my_other_proto.proto: remove method_signature `type` from rpc method `context.subject`.\n"
            + "my_proto.proto L5: remove resource_definition `subject`.\n"
            + "my_proto.proto L12: remove rpc method `context.subject`.\n",
        )

    def test_change_type_major_1(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
            subject="subject",
        )
        dict_arr_output = finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["change_type"], "MAJOR")

    def test_change_type_major_2(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.FEAT_BREAKING,
            subject="subject",
        )
        dict_arr_output = finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["change_type"], "MAJOR")

    def test_change_type_minor(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.FEAT,
            subject="subject",
        )
        dict_arr_output = finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["change_type"], "MINOR")

    def test_change_type_patch(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.FIX,
            subject="subject",
        )
        dict_arr_output = finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["change_type"], "PATCH")

    def test_change_type_none_1(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.DOCS,
            subject="subject",
        )
        dict_arr_output = finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["change_type"], "NONE")

    def test_change_type_none_2(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_REMOVAL,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.CHORE,
            subject="subject",
        )
        dict_arr_output = finding_container.to_dict_arr()
        self.assertEqual(dict_arr_output[0]["change_type"], "NONE")

    def test_human_readable_message_for_all_findings(self):
        finding_container = FindingContainer()
        finding_container.add_finding(
            category=FindingCategory.METHOD_ADDITION,
            proto_file_name="test.proto",
            source_code_line=1,
            conventional_commit_tag=ConventionalCommitTag.FEAT,
            subject="subject",
        )
        message = finding_container.to_human_readable_message(all_changes=True)
        self.assertEqual(
            message, "test.proto L1: add rpc method `.subject`.\n"
        )


if __name__ == "__main__":
    unittest.main()

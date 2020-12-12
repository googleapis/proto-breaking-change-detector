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
import os
from click.testing import CliRunner
from src.cli.detect import detect
from unittest.mock import patch
from io import StringIO


class CliDetectTest(unittest.TestCase):
    COMMON_PROTOS_DIR = os.path.join(os.getcwd(), "api-common-protos")

    def test_descriptor_set_enum(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_descriptor_set_file_path=test/testdata/protos/enum/v1/enum_descriptor_set.pb",
                    "--update_descriptor_set_file_path=test/testdata/protos/enum/v1beta1/enum_descriptor_set.pb",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: An existing Enum `BookType` is removed.\n",
            )

    def test_single_directory_enum(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--update_proto_files=test/testdata/protos/enum/v1beta1/enum_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: An existing Enum `BookType` is removed.\n",
            )

    def test_single_directory_message(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/message/v1",
                    "--update_api_definition_dirs=test/testdata/protos/message/v1beta1",
                    "--original_proto_files=test/testdata/protos/message/v1/message_v1.proto",
                    "--update_proto_files=test/testdata/protos/message/v1beta1/message_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "message_v1beta1.proto L7: Type of an existing field `id` is changed from `int32` to `string`.\n"
                + "message_v1beta1.proto L8: Name of an existing field is changed from `email` to `email_address`.\n"
                + "message_v1beta1.proto L21: Repeated state of an existing field `phones` is changed.\n"
                + "message_v1beta1.proto L22: An existing field `single` is moved out of One-of.\n"
                + "message_v1.proto L18: An existing field `type` is removed.\n",
            )

    def test_single_directory_service(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/service/v1",
                    "--update_api_definition_dirs=test/testdata/protos/service/v1beta1",
                    "--original_proto_files=test/testdata/protos/service/v1/service_v1.proto",
                    "--update_proto_files=test/testdata/protos/service/v1beta1/service_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "service_v1.proto L11: An existing rpc method `shouldRemove` is removed.\n"
                + "service_v1.proto L21: An existing field `page_size` is removed.\n"
                + "service_v1.proto L22: An existing field `page_token` is removed.\n"
                + "service_v1.proto L26: An existing field `content` is removed.\n"
                + "service_v1.proto L27: An existing field `next_page_token` is removed.\n"
                + "service_v1beta1.proto L7: Input type of an existing method `Foo` is changed from `.example.v1.FooRequest` to `.example.v1beta1.FooRequestUpdate`.\n"
                + "service_v1beta1.proto L7: Output type of an existing method `Foo` is changed from `.example.v1.FooResponse` to `.example.v1beta1.FooResponseUpdate`.\n"
                + "service_v1beta1.proto L9: The request streaming type of an existing method `Bar` is changed.\n"
                + "service_v1beta1.proto L9: The response streaming type of an existing method `Bar` is changed.\n"
                + "service_v1beta1.proto L11: The paginated response of an existing method `paginatedMethod` is changed.\n",
            )

    def test_single_directory_service_annotation(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=test/testdata/protos/service_annotation/v1,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=test/testdata/protos/service_annotation/v1beta1,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=test/testdata/protos/service_annotation/v1/service_annotation_v1.proto",
                    "--update_proto_files=test/testdata/protos/service_annotation/v1beta1/service_annotation_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "service_annotation_v1beta1.proto L14: An existing http method of google.api.http annotation is changed for method `Foo`.\n"
                + "service_annotation_v1beta1.proto L18: An existing method_signature for method `Foo` is changed from `content` to `error`.\n"
                + "service_annotation_v1beta1.proto L18: An existing method_signature for method `Foo` is changed from `error` to `content`.\n"
                + "service_annotation_v1beta1.proto L22: An existing http method body of google.api.http annotation is changed for method `Bar`.\n"
                + "service_annotation_v1beta1.proto L26: The metadata_type of an existing LRO operation_info annotation for method `Bar` is changed from `FooMetadata` to `FooMetadataUpdate`.\n"
                + "service_annotation_v1.proto L40: An existing message `FooMetadata` is removed.\n",
            )

    def test_oslogin_proto_alpha(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/cloud/oslogin/v1/oslogin.proto",
                    "--update_proto_files=googleapis/google/cloud/oslogin/v1alpha/oslogin.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/cloud/oslogin/v1/oslogin.proto L34: An exisiting packaging option `Google::Cloud::OsLogin::V1` for `ruby_package` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L41: An existing default host `oslogin.googleapis.com` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L42: An existing oauth_scope `https://www.googleapis.com/auth/cloud-platform` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L42: An existing oauth_scope `https://www.googleapis.com/auth/compute` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L51: An existing method_signature is removed from method `DeletePosixAccount`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L59: An existing method_signature is removed from method `DeleteSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L68: An existing method_signature is removed from method `GetLoginProfile`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L76: An existing method_signature is removed from method `GetSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L87: An existing method_signature is removed from method `ImportSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L98: An existing method_signature is removed from method `UpdateSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L123: A resource reference option of the field `name` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L136: A resource reference option of the field `name` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L147: A resource reference option of the field `name` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L153: An existing field `project_id` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L156: An existing field `system_id` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L166: A resource reference option of the field `name` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L177: A resource reference option of the field `parent` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L202: A resource reference option of the field `name` is removed.\n",
            )

    def test_oslogin_proto_beta(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/cloud/oslogin/v1/oslogin.proto",
                    "--update_proto_files=googleapis/google/cloud/oslogin/v1beta/oslogin.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/cloud/oslogin/v1beta/oslogin.proto L179: Field behavior of an existing field `ssh_public_key` is changed.\n",
            )

    def test_pubsub_proto(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/pubsub/v1beta2/pubsub.proto",
                    "--update_proto_files=googleapis/google/pubsub/v1/pubsub.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/pubsub/v1/pubsub.proto L160: Field behavior of an existing field `name` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L221: Field behavior of an existing field `topic` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L245: Field behavior of an existing field `topic` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L250: Field behavior of an existing field `messages` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L266: Field behavior of an existing field `project` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L267: A resource reference option is added to the field `project`, but it is not defined anywhere\n"
                + "google/pubsub/v1/pubsub.proto L296: Field behavior of an existing field `topic` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L356: Field behavior of an existing field `topic` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L617: Field behavior of an existing field `name` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L623: Field behavior of an existing field `topic` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L880: Field behavior of an existing field `subscription` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L903: Field behavior of an existing field `project` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L904: A resource reference option is added to the field `project`, but it is not defined anywhere\n"
                + "google/pubsub/v1/pubsub.proto L934: Field behavior of an existing field `subscription` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L946: Field behavior of an existing field `subscription` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L958: Field behavior of an existing field `push_config` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L966: Field behavior of an existing field `subscription` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L985: Field behavior of an existing field `max_messages` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L1002: Field behavior of an existing field `subscription` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L1019: Field behavior of an existing field `ack_deadline_seconds` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L1027: Field behavior of an existing field `subscription` is changed.\n"
                + "google/pubsub/v1/pubsub.proto L1036: Field behavior of an existing field `ack_ids` is changed.\n"
                + "google/pubsub/v1beta2/pubsub.proto L369: An existing field `ack_id` is removed.\n",
            )


if __name__ == "__main__":
    unittest.main()

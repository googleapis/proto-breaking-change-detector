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
from click.testing import CliRunner
from src.cli.detect import detect
from unittest.mock import patch
from io import StringIO


class CliDetectTest(unittest.TestCase):
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
                result.output, "enum_v1.proto L5: An Enum `BookType` is removed.\n"
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
                result.output, "enum_v1.proto L5: An Enum `BookType` is removed.\n"
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
                "message_v1beta1.proto L7: Type of an existing field `id` is changed from `TYPE_INT32` to `TYPE_STRING`.\n"
                + "message_v1beta1.proto L8: Name of an existing field is changed from `email` to `email_address`.\n"
                + "message_v1beta1.proto L21: Repeated state of an existing field `phones` is changed from `LABEL_REPEATED` to `LABEL_OPTIONAL`.\n"
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
                + "service_v1beta1.proto L7: Input type of an existing method `Foo` is changed from `FooRequest` to `FooRequestUpdate`.\n"
                + "service_v1beta1.proto L7: Output type of an existing method `Foo` is changed from `FooResponse` to `FooResponseUpdate`.\n"
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
                    "--original_api_definition_dirs=test/testdata/protos/service_annotation/v1",
                    "--update_api_definition_dirs=test/testdata/protos/service_annotation/v1beta1",
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

    def test_mutiple_directories(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1,test/testdata/protos/message/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta1,test/testdata/protos/message/v1beta1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto,test/testdata/protos/message/v1/message_v1.proto",
                    "--update_proto_files=test/testdata/protos/enum/v1beta1/enum_v1beta1.proto,test/testdata/protos/message/v1beta1/message_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "message_v1beta1.proto L7: Type of an existing field `id` is changed from `TYPE_INT32` to `TYPE_STRING`.\n"
                + "message_v1beta1.proto L8: Name of an existing field is changed from `email` to `email_address`.\n"
                + "message_v1beta1.proto L21: Repeated state of an existing field `phones` is changed from `LABEL_REPEATED` to `LABEL_OPTIONAL`.\n"
                + "message_v1beta1.proto L22: An existing field `single` is moved out of One-of.\n"
                + "message_v1.proto L18: An existing field `type` is removed.\n"
                + "enum_v1.proto L5: An Enum `BookType` is removed.\n",
            )


if __name__ == "__main__":
    unittest.main()

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
from src.findings.finding_container import FindingContainer


class CliDetectTest(unittest.TestCase):
    def tearDown(self):
        FindingContainer.reset()

    def test_single_directory(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "test/testdata/protos/example/enum_v1",
                    "test/testdata/protos/example/enum_v1beta1",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output, "enum_v1.proto L5: An Enum BookType is removed\n"
            )

    def test_mutiple_directories(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "test/testdata/protos/example/enum_v1,test/testdata/protos/example/message_v1",
                    "test/testdata/protos/example/enum_v1beta1,test/testdata/protos/example/message_v1beta1",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "message_v1beta1.proto L7: Type of the field is changed, the original is TYPE_INT32, but the updated is TYPE_STRING\n"
                + "message_v1beta1.proto L8: Name of the Field is changed, the original is email, but the updated is email_address\n"
                + "message_v1beta1.proto L21: Repeated state of the Field is changed, the original is LABEL_REPEATED, but the updated is LABEL_OPTIONAL\n"
                + "message_v1beta1.proto L22: The existing field single is moved out of One-of.\n"
                + "message_v1.proto L18: A Field type is removed\n"
                + "enum_v1.proto L5: An Enum BookType is removed\n",
            )


if __name__ == "__main__":
    unittest.main()

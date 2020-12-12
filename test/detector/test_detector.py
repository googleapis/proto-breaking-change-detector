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
from unittest import mock
from io import StringIO
from src.detector.detector import Detector
from google.protobuf import descriptor_pb2 as desc
from test.tools.mock_descriptors import (
    make_file_pb2,
    make_service,
    make_method,
    make_message,
)
from src.detector.options import Options


class DectetorTest(unittest.TestCase):
    def test_detector_basic(self):
        # Mock original and updated FileDescriptorSet.
        L = desc.SourceCodeInfo.Location
        # fmt: off
        locations = [
            L(path=(6, 0, 2, 0), span=(1, 2, 3, 4)),
            L(path=(4, 0), span=(5, 6, 7, 8)),
            L(path=(4, 1), span=(11, 12, 13, 14)),
        ]
        # fmt: on
        input_msg = make_message(name="input", full_name=".example.v1.input")
        output_msg = make_message(name="output", full_name=".example.v1.output")
        service_original = make_service(
            methods=(
                make_method(
                    name="DoThing", input_message=input_msg, output_message=output_msg
                ),
            )
        )
        service_update = make_service()
        file_set_original = desc.FileDescriptorSet(
            file=[
                make_file_pb2(
                    services=[service_original],
                    locations=locations,
                    messages=[input_msg, output_msg],
                )
            ]
        )
        file_set_update = desc.FileDescriptorSet(
            file=[make_file_pb2(services=[service_update])]
        )
        with mock.patch("os.path.isdir") as mocked_isdir:
            with mock.patch("os.path.isfile") as mocked_isfile:
                mocked_isdir.return_value = True
                mocked_isfile.return_value = True
                opts = Options(
                    original_api_definition_dirs="c,d",
                    update_api_definition_dirs="a,b",
                    original_proto_files="pf1, pf2",
                    update_proto_files="pf3, pf4",
                    original_descriptor_set_file_path=None,
                    update_descriptor_set_file_path=None,
                    human_readable_message=True,
                )
        with mock.patch("sys.stdout", new=StringIO()) as fakeOutput:
            Detector(file_set_original, file_set_update, opts).detect_breaking_changes()
            self.assertEqual(
                fakeOutput.getvalue(),
                "my_proto.proto L2: An existing rpc method `DoThing` is removed.\n"
                + "my_proto.proto L6: An existing message `input` is removed.\n"
                + "my_proto.proto L12: An existing message `output` is removed.\n",
            )


if __name__ == "__main__":
    unittest.main()

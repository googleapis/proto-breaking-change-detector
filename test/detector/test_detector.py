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
from unittest import mock
from io import StringIO
from google.protobuf import descriptor_pb2 as desc
from test.tools.mock_descriptors import (
    make_file_pb2,
    make_service,
    make_method,
    make_message,
    make_enum,
)

from proto_bcd.detector.detector import Detector
from proto_bcd.detector.options import Options
from proto_bcd.findings.finding import Finding


class DectetorTest(unittest.TestCase):
    def test_detector_basic(self):
        # Mock original and updated FileDescriptorSet.
        L = desc.SourceCodeInfo.Location
        # fmt: off
        locations = [
            L(path=(6, 0, 2, 0), span=(1, 2, 3, 4)),
            L(path=(4, 0,), span=(5, 6, 7, 8),),
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
        with mock.patch("sys.stdout", new=StringIO()) as fake_output:
            result = Detector(
                file_set_original, file_set_update, opts
            ).detect_breaking_changes()
            self.assertEqual(
                fake_output.getvalue(),
                "my_proto.proto L2: remove rpc method `Placeholder.DoThing`.\n"
                + "my_proto.proto L6: remove message `input`.\n"
                + "my_proto.proto L12: remove message `output`.\n",
            )
            self.assertEqual(len(result), 3)

    def test_detector_without_opts(self):
        # Mock original and updated FileDescriptorSet.
        enum_foo = make_enum(name="foo")
        enum_bar = make_enum(name="bar")
        file_set_original = desc.FileDescriptorSet(
            file=[make_file_pb2(name="original.proto", enums=[enum_foo])]
        )
        file_set_update = desc.FileDescriptorSet(
            file=[make_file_pb2(name="update.proto", enums=[enum_bar])]
        )
        breaking_changes = Detector(
            file_set_original, file_set_update
        ).detect_breaking_changes()
        # Without options, the detector returns an array of actionable Findings.
        self.assertEqual(
            breaking_changes[0].get_message(), "remove enum `foo`."
        )

    def test_detector_all_changes(self):
        # Mock original and updated FileDescriptorSet.
        enum_original = make_enum(name="foo", values=[("A", 1)])
        enum_update = make_enum(name="foo", values=[("A", 1), ("B", 2)])
        file_set_original = desc.FileDescriptorSet(
            file=[make_file_pb2(name="file.proto", enums=[enum_original])]
        )
        file_set_update = desc.FileDescriptorSet(
            file=[make_file_pb2(name="file.proto", enums=[enum_update])]
        )
        breaking_changes = Detector(
            file_set_original, file_set_update
        ).detect_breaking_changes()
        # Without options, the detector returns an array of actionable Findings.
        self.assertEqual(len(breaking_changes), 0)
        all_changes = Detector(file_set_original, file_set_update).detect_all_changes()
        self.assertEqual(len(all_changes), 1)


if __name__ == "__main__":
    unittest.main()

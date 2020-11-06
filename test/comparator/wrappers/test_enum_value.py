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
from test.tools.mock_descriptors import make_enum_value
from google.protobuf import descriptor_pb2


class EnumValueTest(unittest.TestCase):
    def test_basic_properties(self):
        enum_value = make_enum_value("FOO", 1)
        self.assertEqual(enum_value.name, "FOO")
        self.assertEqual(enum_value.number, 1)
        self.assertEqual(enum_value.proto_file_name, "foo")
        self.assertEqual(
            enum_value.source_code_line,
            "No source code line can be identified by path ().",
        )
        self.assertEqual(enum_value.path, ())

    def test_extra_properties(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        location = L(path=(4, 0, 2, 0), span=(1, 2, 3, 4))
        enum_value = make_enum_value(
            name="FOO",
            number=1,
            proto_file_name="foo.proto",
            source_code_locations={(4, 0, 2, 0): location},
            path=(4, 0, 2, 0),
        )
        self.assertEqual(enum_value.name, "FOO")
        self.assertEqual(enum_value.number, 1)
        self.assertEqual(enum_value.proto_file_name, "foo.proto")
        self.assertEqual(
            enum_value.source_code_line,
            2,
        )
        self.assertEqual(enum_value.path, (4, 0, 2, 0))


if __name__ == "__main__":
    unittest.main()

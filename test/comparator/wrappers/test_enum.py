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
from test.tools.mock_descriptors import make_enum
from google.protobuf import descriptor_pb2


class EnumTest(unittest.TestCase):
    def test_basic_properties(self):
        enum = make_enum("Foo")
        self.assertEqual(enum.name, "Foo")
        self.assertEqual(enum.proto_file_name, "foo")
        self.assertEqual(enum.path, ())
        self.assertEqual(
            enum.source_code_line,
            "No source code line can be identified by path ().",
        )

    def test_enum_value_properties(self):
        enum_type = make_enum(
            name="Irrelevant",
            values=(
                ("RED", 1),
                ("GREEN", 2),
                ("BLUE", 3),
            ),
        )
        self.assertEqual(len(enum_type.values), 3)
        for ev, expected in zip(enum_type.values.values(), ("RED", "GREEN", "BLUE")):
            self.assertEqual(ev.name, expected)

    def test_source_code_properties(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        # fmt: off
        locations = [L(path=(4, 0,), span=(1, 2, 3, 4))]
        enum = make_enum(
            name="Foo",
            proto_file_name="test.proto",
            locations=locations,
            path=(4, 0,),
        )

        # fmt: on
        self.assertEqual(enum.name, "Foo")
        self.assertEqual(enum.values, {})
        self.assertEqual(enum.proto_file_name, "test.proto")
        self.assertEqual(
            enum.source_code_line,
            2,
        )
        self.assertEqual(enum.path, (4, 0))


if __name__ == "__main__":
    unittest.main()

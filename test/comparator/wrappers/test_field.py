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
from test.tools.mock_descriptors import make_field
from google.protobuf import descriptor_pb2
from google.api import field_behavior_pb2
from google.api import resource_pb2


class FieldTest(unittest.TestCase):
    def test_basic_properties(self):
        field = make_field("Foo")
        self.assertEqual(field.name, "Foo")
        self.assertEqual(field.number, 1)
        self.assertEqual(field.proto_type.value, "message")
        self.assertEqual(field.oneof, False)
        self.assertEqual(field.proto_file_name, "foo")
        self.assertEqual(field.api_version, None)
        self.assertEqual(field.map_entry, None)

    def test_api_version(self):
        field = make_field("Foo", api_version="v1")
        self.assertEqual(field.name, "Foo")
        self.assertEqual(field.api_version, "v1")

    def test_field_is_primitive(self):
        primitive_field = make_field(proto_type="TYPE_INT32")
        self.assertEqual(primitive_field.is_primitive_type, True)
        self.assertEqual(primitive_field.proto_type.value, "int32")
        self.assertEqual(make_field(proto_type="TYPE_FLOAT").proto_type.value, "float")
        self.assertEqual(make_field(proto_type="TYPE_INT64").proto_type.value, "int64")
        self.assertEqual(make_field(proto_type="TYPE_BOOL").proto_type.value, "bool")
        self.assertEqual(
            make_field(proto_type="TYPE_STRING").proto_type.value, "string"
        )
        self.assertEqual(make_field(proto_type="TYPE_BYTES").proto_type.value, "bytes")

    def test_field_not_primitive(self):
        non_primitive_field = make_field(
            proto_type="TYPE_ENUM",
            type_name=".example.Enum",
        )
        self.assertEqual(non_primitive_field.is_primitive_type, False)
        self.assertEqual(non_primitive_field.proto_type.value, "enum")
        self.assertEqual(non_primitive_field.type_name.value, ".example.Enum")

    def test_repeated(self):
        field = make_field(repeated=True)
        self.assertTrue(field.repeated.value)

    def test_not_repeated(self):
        field = make_field(repeated=False)
        self.assertFalse(field.repeated.value)

    def test_required(self):
        field = make_field(required=True)
        self.assertTrue(field.required.value)

    def test_not_required(self):
        field = make_field()
        self.assertEqual(field.required.value, False)

    def test_oneof(self):
        field = make_field(oneof_name="oneof_field", oneof_index=0)
        self.assertTrue(field.oneof)
        self.assertEqual(field.oneof_name, "oneof_field")

    def test_resource_reference(self):
        options = descriptor_pb2.FieldOptions()
        resource_ref = options.Extensions[resource_pb2.resource_reference]
        resource_ref.child_type = "foo/{foo}"
        field = make_field(options=options)
        self.assertEqual(field.resource_reference.value.child_type, "foo/{foo}")
        self.assertEqual(field.child_type, True)

    def test_source_code_line(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        locations = [
            L(path=(4, 0, 2, 1), span=(1, 2, 3, 4)),
        ]
        field = make_field(
            proto_file_name="test.proto",
            locations=locations,
            path=(4, 0, 2, 1),
        )
        self.assertEqual(field.source_code_line, 2)
        self.assertEqual(field.proto_file_name, "test.proto")

    def test_map_entry(self):
        # Key in map fields cannot be float/double, bytes, enums or message types.
        key_field = make_field(name="key", number=1, proto_type="TYPE_STRING")
        value_field = make_field(name="value", number=2, type_name=".example.foo")
        map_field = make_field(
            name="map_field",
            proto_type="TYPE_MESSAGE",
            type_name="MapFieldEntry",
            map_entry={"key": key_field, "value": value_field},
        )
        self.assertTrue(map_field.is_map_type)
        self.assertTrue(map_field.map_entry_type)
        self.assertEqual(map_field.map_entry_type["key"], "string")
        self.assertEqual(map_field.map_entry_type["value"], ".example.foo")


if __name__ == "__main__":
    unittest.main()

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
from test.tools.invoker import UnittestInvoker
from src.comparator.wrappers import FileSet


class WrappersTest(unittest.TestCase):
    # This is for tesing the behavior of classes in src.comparator.wrapper.
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet out of it.

    _INVOKER = UnittestInvoker(["wrappers.proto"], "wrappers_descriptor_set.pb", True)
    _FILE_SET = FileSet(_INVOKER.run())

    def test_file_set_wrapper(self):
        self.assertTrue(self._FILE_SET.messages_map)
        self.assertTrue(self._FILE_SET.enums_map)
        self.assertTrue(self._FILE_SET.services_map)
        resources_database = self._FILE_SET.resources_database
        self.assertEqual(
            resources_database.types["example.googleapis.com/t1"].pattern,
            ["foo/{foo}", "foo/{foo}/bar/{bar}/t1"],
        )

    def test_service_wrapper(self):
        service = self._FILE_SET.services_map["Example"]
        # Service `Example` is defined at Line19 in .proto file.
        self.assertEqual(service.source_code_line, 19)
        self.assertEqual(service.proto_file_name, "wrappers.proto")
        foo_method = service.methods["Foo"]
        bar_method = service.methods["Bar"]
        self.assertEqual(foo_method.input.value, "FooRequest")
        self.assertEqual(foo_method.output.value, "FooResponse")
        self.assertEqual(foo_method.paged_result_field, None)
        self.assertEqual(foo_method.method_signatures.value, ["content", "error"])
        self.assertEqual(
            foo_method.http_annotation.value["http_uri"], "/v1/example:foo"
        )

        # Method `Foo` is defined at Line21 in .proto file.
        self.assertEqual(foo_method.source_code_line, 21)
        self.assertEqual(foo_method.proto_file_name, "wrappers.proto")

        self.assertEqual(bar_method.input.value, "FooRequest")
        self.assertEqual(bar_method.output.value, ".google.longrunning.Operation")
        self.assertEqual(bar_method.paged_result_field, None)
        self.assertTrue(bar_method.longrunning)
        self.assertEqual(
            bar_method.lro_annotation.value["response_type"], "FooResponse"
        )
        self.assertEqual(
            bar_method.lro_annotation.value["metadata_type"], "FooMetadata"
        )
        self.assertEqual(
            bar_method.http_annotation.value["http_uri"], "/v1/example:bar"
        )
        # Method `Bar` is defined at Line29 in .proto file.
        self.assertEqual(bar_method.source_code_line, 29)

    def test_message_wrapper(self):
        messages_map = self._FILE_SET.messages_map
        foo_request_message = messages_map["FooRequest"]
        # Message `FooRequest` is defined at Line41 in .proto file.
        self.assertEqual(foo_request_message.source_code_line, 41)
        self.assertTrue(foo_request_message.nested_messages["NestedMessage"])
        self.assertEqual(foo_request_message.proto_file_name, "wrappers.proto")
        # Nested message `NestedMessage` is defined at Line50 in .proto file.
        self.assertEqual(
            foo_request_message.nested_messages["NestedMessage"].source_code_line, 50
        )
        self.assertTrue(foo_request_message.nested_enums["NestedEnum"])
        # Nested enum `NestedEnum` is defined at Line51 in .proto file.
        self.assertEqual(
            foo_request_message.nested_enums["NestedEnum"].source_code_line, 51
        )
        self.assertEqual(foo_request_message.oneof_fields[0].name, "content")
        self.assertEqual(foo_request_message.oneof_fields[1].name, "error")
        # Oneof field `content` and `error` are defined at Line47,48 in .proto file.
        self.assertEqual(foo_request_message.oneof_fields[0].source_code_line, 47)
        self.assertEqual(foo_request_message.oneof_fields[1].source_code_line, 48)
        resource = foo_request_message.resource
        self.assertEqual(resource.pattern, ["foo/{foo}/bar/{bar}"])
        self.assertEqual(resource.type, "example.googleapis.com/Foo")

    def test_field_wrapper(self):
        foo_response_message = self._FILE_SET.messages_map["FooResponse"]
        enum_field = foo_response_message.fields[1]
        self.assertEqual(enum_field.label.value, "LABEL_OPTIONAL")
        self.assertEqual(enum_field.required, False)
        self.assertEqual(enum_field.proto_type.value, "TYPE_ENUM")
        self.assertEqual(enum_field.oneof, False)
        self.assertEqual(enum_field.child_type, True)
        self.assertEqual(
            enum_field.resource_reference.value.child_type, "example.googleapis.com/t1"
        )
        # Enum `enum_field` is defined at Line57 in .proto file.
        self.assertEqual(enum_field.source_code_line, 57)
        self.assertEqual(enum_field.proto_file_name, "wrappers.proto")

    def test_enum_wrapper(self):
        enum = self._FILE_SET.enums_map["Enum1"]
        self.assertEqual(enum.values[0].name, "a")
        self.assertEqual(enum.values[1].name, "b")
        # EnumValue `a` and `b` are defined at Line57 in .proto file.
        self.assertEqual(enum.values[0].source_code_line, 65)
        self.assertEqual(enum.values[1].source_code_line, 66)
        self.assertEqual(enum.values[0].proto_file_name, "wrappers.proto")

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER.cleanup()


if __name__ == "__main__":
    unittest.main()

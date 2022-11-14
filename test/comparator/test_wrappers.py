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
import os
from proto_bcd.detector.loader import Loader
from proto_bcd.comparator.wrappers import FileSet, Field


class WrappersTest(unittest.TestCase):
    # This is for tesing the behavior of classes in proto_bcd.comparator.wrapper.
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet out of it.
    _CURRENT_DIR = os.getcwd()
    COMMON_PROTOS_DIR = os.path.join(_CURRENT_DIR, "api-common-protos")

    _INVOKER = Loader(
        proto_definition_dirs=[
            os.path.join(_CURRENT_DIR, "test/testdata/protos/example/"),
            COMMON_PROTOS_DIR,
        ],
        proto_files=[
            os.path.join(_CURRENT_DIR, "test/testdata/protos/example/wrappers.proto")
        ],
        descriptor_set=None,
    )
    _FILE_SET = FileSet(_INVOKER.get_descriptor_set())

    def test_file_set_wrapper(self):
        self.assertTrue(self._FILE_SET.messages_map)
        self.assertTrue(self._FILE_SET.enums_map)
        self.assertTrue(self._FILE_SET.services_map)
        resources_database = self._FILE_SET.resources_database
        self.assertEqual(
            resources_database.types["example.googleapis.com/t1"].value.pattern,
            ["foo/{foo}", "foo/{foo}/bar/{bar}/t1"],
        )
        # The service from imported dependency `google/longrunning/operations`
        # is included in the file set.
        self.assertEqual(list(self._FILE_SET.services_map.keys()), ["Example"])
        self.assertEqual(self._FILE_SET.root_package, "example.v1alpha")
        self.assertEqual(len(self._FILE_SET.definition_files), 1)
        self.assertEqual(self._FILE_SET.definition_files[0].name, "wrappers.proto")
        self.assertEqual(self._FILE_SET.api_version, "v1alpha")
        # Check the global messages/enums map
        self.assertEqual(
            [
                message_name
                for message_name in self._FILE_SET.global_messages_map.keys()
                if message_name.startswith(".example.v1alpha")
            ],
            [
                ".example.v1alpha.MapMessage",
                ".example.v1alpha.FooMetadata",
                ".example.v1alpha.FooResponse",
                ".example.v1alpha.FooRequest",
                ".example.v1alpha.FooRequest.NestedMessage",
            ],
        )
        self.assertEqual(
            [
                message_name
                for message_name in self._FILE_SET.global_messages_map.keys()
                if message_name.startswith(".google.api")
            ],
            [
                ".google.api.ResourceReference",
                ".google.api.ResourceDescriptor",
                ".google.api.CustomHttpPattern",
                ".google.api.HttpRule",
                ".google.api.Http",
            ],
        )
        self.assertEqual(
            [
                enum_name
                for enum_name in self._FILE_SET.global_enums_map.keys()
                if enum_name.startswith(".example.v1alpha")
            ],
            [
                ".example.v1alpha.Enum1",
                ".example.v1alpha.FooRequest.NestedEnum",
            ],
        )
        # Check the used messages map.
        used_messages_name = [
            ".example.v1alpha.FooRequest",
            ".example.v1alpha.FooResponse",
            ".google.longrunning.Operation",
            ".example.v1alpha.FooMetadata",
            ".example.v1alpha.MapMessage",
            ".google.rpc.Status",
        ]
        self.assertTrue(
            set(self._FILE_SET.messages_map.keys())
            <= set(self._FILE_SET.global_messages_map.keys())
        )
        self.assertEqual(list(self._FILE_SET.messages_map.keys()), used_messages_name)
        self.assertEqual(
            list(self._FILE_SET.enums_map.keys()), [".example.v1alpha.Enum1"]
        )

    def test_service_wrapper(self):
        service = self._FILE_SET.services_map["Example"]
        # Service `Example` is defined at Line20 in .proto file.
        self.assertEqual(service.source_code_line, 20)
        self.assertEqual(service.api_version, "v1alpha")
        self.assertEqual(service.proto_file_name, "wrappers.proto")
        self.assertEqual(len(service.oauth_scopes), 1)
        self.assertEqual(
            service.oauth_scopes[0].value,
            "https://www.googleapis.com/auth/cloud-platform",
        )
        self.assertEqual(service.oauth_scopes[0].source_code_line, 21)
        foo_method = service.methods["Foo"]
        bar_method = service.methods["Bar"]
        self.assertEqual(foo_method.input.value, ".example.v1alpha.FooRequest")
        self.assertEqual(foo_method.output.value, ".example.v1alpha.FooResponse")
        self.assertEqual(foo_method.paged_result_field, None)
        # The method signature is defined at Line28 in the proto file.
        self.assertEqual(foo_method.method_signatures.source_code_line, 28)
        self.assertEqual(foo_method.method_signatures.value, [("content", "error")])
        self.assertEqual(
            foo_method.http_annotation.value["http_uri"], "/v1/example:foo"
        )

        # Method `Foo` is defined at Line23 in .proto file.
        self.assertEqual(foo_method.source_code_line, 23)
        self.assertEqual(foo_method.proto_file_name, "wrappers.proto")

        self.assertEqual(bar_method.input.value, ".example.v1alpha.FooRequest")
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
        # Method `Bar` is defined at Line31 in .proto file.
        self.assertEqual(bar_method.source_code_line, 31)

    def test_message_wrapper(self):
        messages_map = self._FILE_SET.messages_map
        foo_request_message = messages_map[".example.v1alpha.FooRequest"]
        # Message `FooRequest` is defined at Line43 in .proto file.
        self.assertEqual(foo_request_message.source_code_line, 43)
        self.assertEqual(foo_request_message.api_version, "v1alpha")
        self.assertTrue(foo_request_message.nested_messages["NestedMessage"])
        self.assertEqual(foo_request_message.proto_file_name, "wrappers.proto")
        self.assertEqual(list(foo_request_message.oneofs.keys()), ["response"])
        # Nested message `NestedMessage` is defined at Line52 in .proto file.
        self.assertEqual(
            foo_request_message.nested_messages["NestedMessage"].source_code_line, 52
        )
        self.assertTrue(foo_request_message.nested_enums["NestedEnum"])
        # Nested enum `NestedEnum` is defined at Line53 in .proto file.
        self.assertEqual(
            foo_request_message.nested_enums["NestedEnum"].source_code_line, 53
        )
        resource = foo_request_message.resource
        self.assertEqual(resource.value.pattern, ["foo/{foo}/bar/{bar}"])
        self.assertEqual(resource.value.type, "example.googleapis.com/Foo")

        # The message has auto-generated map entries (nested type) for fields that is map type.
        map_message = messages_map[".example.v1alpha.MapMessage"]
        self.assertEqual(len(map_message.fields.keys()), 1)
        self.assertEqual(map_message.fields[1].name, "first_field")
        self.assertEqual(list(map_message.map_entries.keys()), ["FirstFieldEntry"])
        self.assertTrue(
            isinstance(map_message.map_entries["FirstFieldEntry"]["key"], Field)
        )
        self.assertTrue(
            isinstance(map_message.map_entries["FirstFieldEntry"]["value"], Field)
        )
        # It should not put into the nested message, so the nested message map is empty.
        self.assertFalse(map_message.nested_messages)

    def test_field_wrapper(self):
        foo_request_message = self._FILE_SET.messages_map[".example.v1alpha.FooRequest"]
        # Oneof field `content` and `error` are defined at Line49,50 in .proto file.
        content_field_oneof = foo_request_message.fields[1]
        error_field_oneof = foo_request_message.fields[2]
        self.assertEqual(content_field_oneof.oneof_name, "response")
        self.assertEqual(error_field_oneof.oneof_name, "response")
        self.assertFalse(content_field_oneof.map_entry_type)
        self.assertEqual(content_field_oneof.source_code_line, 49)
        self.assertEqual(error_field_oneof.source_code_line, 50)
        foo_response_message = self._FILE_SET.messages_map[
            ".example.v1alpha.FooResponse"
        ]
        enum_field = foo_response_message.fields[1]
        self.assertEqual(enum_field.api_version, "v1alpha")
        self.assertFalse(enum_field.repeated.value)
        self.assertFalse(enum_field.required.value)
        self.assertEqual(enum_field.proto_type.value, "enum")
        self.assertEqual(enum_field.type_name.value, ".example.v1alpha.Enum1")
        self.assertEqual(enum_field.is_primitive_type, False)
        self.assertEqual(enum_field.oneof, False)
        self.assertEqual(enum_field.child_type, True)
        self.assertEqual(
            enum_field.resource_reference.value.child_type, "example.googleapis.com/t1"
        )
        # Enum `enum_field` is defined at Line58 in .proto file.
        self.assertEqual(enum_field.source_code_line, 59)
        self.assertEqual(enum_field.proto_file_name, "wrappers.proto")

        foo_metadata_message = self._FILE_SET.messages_map[
            ".example.v1alpha.FooMetadata"
        ]
        # Field `name` has `google.api.field_behavior` option as `required`.
        name_field = foo_metadata_message.fields[1]
        self.assertEqual(name_field.name, "name")
        self.assertFalse(name_field.repeated.value)
        self.assertTrue(name_field.required.value)

        map_field = self._FILE_SET.messages_map[".example.v1alpha.MapMessage"].fields[1]
        self.assertTrue(map_field.map_entry)
        self.assertTrue(map_field.is_map_type)
        self.assertEqual(map_field.map_entry_type["key"], "string")
        self.assertEqual(
            map_field.map_entry_type["value"], ".example.v1alpha.FooMetadata"
        )

    def test_enum_wrapper(self):
        enum = self._FILE_SET.enums_map[".example.v1alpha.Enum1"]
        self.assertEqual(enum.values["a"].number, 0)
        self.assertEqual(enum.values["b"].number, 1)
        # EnumValue `a` and `b` are defined at Line71 in .proto file.
        self.assertEqual(enum.values["a"].source_code_line, 71)
        self.assertEqual(enum.values["b"].source_code_line, 72)
        self.assertEqual(enum.values["a"].proto_file_name, "wrappers.proto")


if __name__ == "__main__":
    unittest.main()

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
from test.tools.mock_descriptors import (
    make_file_set,
    make_service,
    make_method,
    make_enum,
    make_message,
    make_field,
    make_file_pb2,
)
from google.api import resource_pb2
from google.protobuf import descriptor_pb2

from src.comparator.wrappers import FileSet


class FileSetTest(unittest.TestCase):
    def test_file_set_properties(self):
        input_message = make_message(name="request", full_name=".example.v1.request")
        output_message = make_message(name="response", full_name=".example.v1.response")
        messages = [
            make_message(
                "InnerMessage",
                fields=(
                    make_field(
                        name="hidden_message", number=1, type_name=".example.v1.request"
                    ),
                ),
                full_name=".example.v1.InnerMessage",
            ),
            input_message,
            output_message,
        ]
        services = [
            make_service(
                name="ThingDoer",
                methods=(
                    make_method(
                        name="DoThing",
                        input_message=input_message,
                        output_message=output_message,
                    ),
                ),
            )
        ]
        enums = [
            make_enum(
                name="Irrelevant",
                values=(
                    ("RED", 1),
                    ("GREEN", 2),
                    ("BLUE", 3),
                ),
            )
        ]
        file_foo = make_file_pb2(
            name="foo.proto",
            package="example.v1",
            services=services,
            enums=enums,
            dependency=["bar.proto"],
        )
        file_bar = make_file_pb2(
            name="bar.proto", package="example.v1", messages=messages
        )
        file_set = make_file_set(files=[file_bar, file_foo])
        # Default to be empty.
        self.assertFalse(file_set.packaging_options_map)
        self.assertEqual(
            list(file_set.messages_map.keys()),
            [".example.v1.InnerMessage", ".example.v1.request", ".example.v1.response"],
        )
        self.assertEqual(list(file_set.enums_map.keys()), [".example.v1.Irrelevant"])
        self.assertEqual(list(file_set.services_map.keys()), ["ThingDoer"])
        self.assertEqual(
            file_set.messages_map[".example.v1.InnerMessage"].fields[1].name,
            "hidden_message",
        )
        self.assertEqual(
            file_set.enums_map[".example.v1.Irrelevant"].values[2].name, "GREEN"
        )
        self.assertEqual(
            list(file_set.services_map["ThingDoer"].methods.keys()),
            ["DoThing"],
        )
        self.assertEqual(
            list(file_set.global_enums_map.keys()), [".example.v1.Irrelevant"]
        )
        self.assertEqual(
            list(file_set.global_messages_map.keys()),
            [".example.v1.response", ".example.v1.request", ".example.v1.InnerMessage"],
        )

    def test_file_set_resources(self):
        options = descriptor_pb2.FileOptions()
        options.Extensions[resource_pb2.resource_definition].append(
            resource_pb2.ResourceDescriptor(
                type="example.v1/Foo",
                pattern=["foo/{foo}"],
            )
        )
        # File1 with file-level resource definition `example.v1/Foo`.
        file1 = make_file_pb2(
            name="foo.proto",
            package=".example.v1",
            dependency=["bar.proto"],
            options=options,
        )
        # File2 with resource definition in message and nested message.
        message_options = descriptor_pb2.MessageOptions()
        resource = message_options.Extensions[resource_pb2.resource]
        resource.pattern.append("user/{user}")
        resource.pattern.append("user/{user}/bar/")
        resource.type = "example.v1/Bar"

        nested_message_options = descriptor_pb2.MessageOptions()
        resource = nested_message_options.Extensions[resource_pb2.resource]
        resource.pattern.append("tests/{test}/")
        resource.type = "example.v1/Test"
        nesed_message = make_message("nested_message", options=nested_message_options)
        message = make_message(
            name="outer_message",
            nested_messages=[nesed_message],
            options=message_options,
        )
        file2 = make_file_pb2(
            name="bar.proto", package=".example.bar", messages=[message]
        )
        file_set = make_file_set(files=[file1, file2])
        # All resources should be registered in the database.
        resource_types = file_set.resources_database.types
        resource_patterns = file_set.resources_database.patterns
        self.assertEqual(
            list(resource_types.keys()),
            ["example.v1/Foo", "example.v1/Bar", "example.v1/Test"],
        )
        self.assertEqual(
            list(resource_patterns.keys()),
            ["foo/{foo}", "user/{user}", "user/{user}/bar/", "tests/{test}/"],
        )
        # Check used resources database.
        # File1 depends on file2, but they are not in the same package, only file1
        # is API definition file. So only resources in file1 are in used_resource_database.
        self.assertEqual(
            list(file_set.used_resources_database.types.keys()), ["example.v1/Foo"]
        )
        self.assertEqual(
            list(file_set.used_resources_database.patterns.keys()), ["foo/{foo}"]
        )

    def test_file_set_source_code_location(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        locations = [
            L(path=(4, 0, 2, 0, 5), span=(5, 2, 3, 4)),
            L(path=(4, 0, 3, 0), span=(6, 1, 2, 4)),
            L(path=(4, 0, 4, 0), span=(7, 1, 2, 4)),
            L(path=(4, 0, 4, 0, 2, 1), span=(9, 1, 2, 4)),
        ]
        messages = [
            make_message(
                "OuterMessage",
                fields=(
                    make_field(
                        name="hidden_message",
                        number=1,
                    ),
                ),
                nested_messages=(make_message(name="InterMessage"),),
                nested_enums=(
                    make_enum(
                        name="InterEnum",
                        values=(
                            ("RED", 1),
                            ("GREEN", 2),
                            ("BLUE", 3),
                        ),
                    ),
                ),
            )
        ]

        file_pb2 = make_file_pb2(messages=messages, locations=locations)
        file_set = make_file_set(files=[file_pb2])
        self.assertEqual(
            file_set.messages_map[".example.v1.OuterMessage"]
            .fields[1]
            .proto_type.source_code_line,
            6,
        )
        self.assertEqual(
            file_set.messages_map[".example.v1.OuterMessage"]
            .nested_messages["InterMessage"]
            .source_code_line,
            7,
        )
        self.assertEqual(
            file_set.messages_map[".example.v1.OuterMessage"]
            .nested_enums["InterEnum"]
            .source_code_line,
            8,
        )
        self.assertEqual(
            file_set.messages_map[".example.v1.OuterMessage"]
            .nested_enums["InterEnum"]
            .values[2]
            .source_code_line,
            10,
        )

    def test_file_set_packaging_options(self):
        option1 = descriptor_pb2.FileOptions()
        option1.java_package = "com.google.example.v1"
        option1.php_namespace = "Google\\Cloud\\Example\\V1"
        option1.php_metadata_namespace = "php_metadata_namespace"
        option1.php_class_prefix = "php_class_prefix"
        option1.ruby_package = "ruby_package"
        option1.java_outer_classname = "Foo"
        option1.go_package = "go_package"
        option1.csharp_namespace = "csharp_namespace"
        option1.swift_prefix = "swift_prefix"

        option2 = descriptor_pb2.FileOptions()
        option2.java_outer_classname = "Bar"
        # Two proto files have the same packging options.
        file1 = make_file_pb2(name="proto1", options=option1)
        file2 = make_file_pb2(name="proto2", options=option2)
        file_set = make_file_set(files=[file1, file2])
        self.assertTrue(file_set.packaging_options_map)
        # fmt: off
        self.assertEqual(
            list(file_set.packaging_options_map["java_package"].keys()),
            ["com.google.example.v1"],
        )
        self.assertEqual(
            file_set.packaging_options_map["java_package"][
                "com.google.example.v1"
            ].path, (8, 1,),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["php_namespace"].keys()),
            ["Google\\Cloud\\Example\\V1"],
        )
        self.assertEqual(
            file_set.packaging_options_map["php_namespace"][
                "Google\\Cloud\\Example\\V1"
            ].path, (8, 41,),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["java_outer_classname"].keys()),
            ["Foo", "Bar"],
        )
        self.assertEqual(
            file_set.packaging_options_map["java_outer_classname"]["Foo"].path,
            (8, 8),
        )
        self.assertEqual(
            file_set.packaging_options_map["java_outer_classname"]["Bar"].path,
            (8, 8),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["php_metadata_namespace"].keys()),
            ["php_metadata_namespace"],
        )
        self.assertEqual(
            file_set.packaging_options_map["php_metadata_namespace"][
                "php_metadata_namespace"
            ].path,
            (8, 44),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["php_class_prefix"].keys()),
            ["php_class_prefix"],
        )
        self.assertEqual(
            file_set.packaging_options_map["php_class_prefix"]["php_class_prefix"].path,
            (8, 40),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["ruby_package"].keys()),
            ["ruby_package"],
        )
        self.assertEqual(
            file_set.packaging_options_map["ruby_package"]["ruby_package"].path,
            (8, 45),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["go_package"].keys()),
            ["go_package"],
        )
        self.assertEqual(
            file_set.packaging_options_map["go_package"]["go_package"].path,
            (8, 11),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["csharp_namespace"].keys()),
            ["csharp_namespace"],
        )
        self.assertEqual(
            file_set.packaging_options_map["csharp_namespace"]["csharp_namespace"].path,
            (8, 37),
        )
        self.assertEqual(
            list(file_set.packaging_options_map["swift_prefix"].keys()),
            ["swift_prefix"],
        )
        self.assertEqual(
            file_set.packaging_options_map["swift_prefix"]["swift_prefix"].path,
            (8, 39),
        )
        # fmt: on

    def test_file_set_api_version(self):
        dep1 = make_file_pb2(name="dep1", package=".example.external")
        dep2 = make_file_pb2(name="dep2", package=".example.external")
        file1 = make_file_pb2(
            name="proto1", dependency=["dep1", "dep2"], package=".example.common"
        )
        file2 = make_file_pb2(
            name="proto2", dependency=["proto1"], package=".example.v1beta"
        )

        file_set = make_file_set(files=[file1, file2, dep1, dep2])
        self.assertEqual(file_set.api_version, "v1beta")

    def test_file_set_root_package(self):
        dep1 = make_file_pb2(name="dep1", package="example.external")
        dep2 = make_file_pb2(name="dep2", package="example.external")
        file1 = make_file_pb2(
            name="proto1", dependency=["dep1", "dep2"], package="example.common"
        )
        file2 = make_file_pb2(
            name="proto2", dependency=["proto1"], package="example.tutorial"
        )
        file3 = make_file_pb2(
            name="proto3", dependency=["proto2", "dep1"], package="example.tutorial"
        )
        file_set = make_file_set(files=[file1, file2, file3, dep1, dep2])
        self.assertEqual(file_set.root_package, "example.tutorial")
        # The package name `example.tutorial` does not have any match for a version.
        self.assertFalse(file_set.api_version)
        # The `proto2` and `proto3` are API definition files, others are dependencies.
        self.assertEqual(
            [f.name for f in file_set.definition_files], ["proto2", "proto3"]
        )
        # If the files are totally not related, the root_package will be the first file package.
        file_set = make_file_set(files=[dep1, dep2])
        self.assertEqual(file_set.root_package, "example.external")
        self.assertFalse(file_set.api_version)

    def test_get_root_package(self):
        common = descriptor_pb2.FileDescriptorProto(
            name="google/cloud/common_resources.proto",
            package="google.cloud",
        )
        speech_resource = descriptor_pb2.FileDescriptorProto(
            name="google/cloud/speech/v1/resource.proto",
            package="google.cloud.speech.v1",
        )
        speech_with_dep = descriptor_pb2.FileDescriptorProto(
            name="google/cloud/speech/v1/cloud_speech.proto",
            package="google.cloud.speech.v1",
            dependency=["google/cloud/speech/v1/resource.proto"],
        )
        speech_no_dep = descriptor_pb2.FileDescriptorProto(
            name="google/cloud/speech/v1/cloud_speech.proto",
            package="google.cloud.speech.v1",
        )
        self.assertEqual(
            FileSet.get_root_package(
                descriptor_pb2.FileDescriptorSet(
                    file=[common, speech_with_dep, speech_resource]
                )
            ),
            "google.cloud.speech.v1",
        )
        self.assertEqual(
            FileSet.get_root_package(
                descriptor_pb2.FileDescriptorSet(file=[common, speech_no_dep])
            ),
            "google.cloud.speech.v1",
        )
        self.assertEqual(
            FileSet.get_root_package(descriptor_pb2.FileDescriptorSet(file=[common])),
            "",
        )


if __name__ == "__main__":
    unittest.main()

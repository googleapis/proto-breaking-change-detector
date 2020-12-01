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


class FileSetTest(unittest.TestCase):
    def test_file_set_properties(self):
        services = [
            make_service(
                name="ThingDoer",
                methods=(
                    make_method(
                        name="DoThing",
                    ),
                    make_method(
                        name="Jump",
                    ),
                    make_method(
                        name="Yawn",
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
        messages = [
            make_message(
                "InnerMessage",
                fields=(
                    make_field(
                        name="hidden_message",
                        number=1,
                    ),
                ),
            )
        ]
        file_foo = make_file_pb2(
            name="foo.proto", package=".example.v1", services=services, enums=enums
        )
        file_bar = make_file_pb2(
            name="bar.proto", package=".example.v1", messages=messages
        )
        file_set = make_file_set(files=[file_bar, file_foo])
        # Default to be empty.
        self.assertFalse(file_set.packaging_options_map)
        self.assertEqual(list(file_set.messages_map.keys()), ["InnerMessage"])
        self.assertEqual(list(file_set.enums_map.keys()), ["Irrelevant"])
        self.assertEqual(list(file_set.services_map.keys()), ["ThingDoer"])
        self.assertEqual(
            file_set.messages_map["InnerMessage"].fields[1].name, "hidden_message"
        )
        self.assertEqual(file_set.enums_map["Irrelevant"].values[2].name, "GREEN")
        self.assertEqual(
            list(file_set.services_map["ThingDoer"].methods.keys()),
            ["DoThing", "Jump", "Yawn"],
        )

    def test_file_set_resources(self):
        options = descriptor_pb2.FileOptions()
        options.Extensions[resource_pb2.resource_definition].append(
            resource_pb2.ResourceDescriptor(
                type="example.v1/Bar",
                pattern=["foo/{foo}/bar/{bar}", "foo/{foo}/bar"],
            )
        )
        message_options = descriptor_pb2.MessageOptions()
        resource = message_options.Extensions[resource_pb2.resource]
        resource.pattern.append("foo/{foo}/")
        resource.type = "example.v1/Foo"
        nesed_message = make_message("Test", options=message_options)
        message = make_message(nested_messages=[nesed_message])
        file_pb2 = make_file_pb2(
            name="foo.proto", package=".example.v1", options=options, messages=[message]
        )
        file_set = make_file_set(files=[file_pb2])
        resource_types = file_set.resources_database.types
        resource_patterns = file_set.resources_database.patterns
        self.assertEqual(
            list(resource_types.keys()), ["example.v1/Bar", "example.v1/Foo"]
        )
        self.assertEqual(
            list(resource_patterns.keys()),
            ["foo/{foo}/bar/{bar}", "foo/{foo}/bar", "foo/{foo}/"],
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
            file_set.messages_map["OuterMessage"].fields[1].proto_type.source_code_line,
            6,
        )
        self.assertEqual(
            file_set.messages_map["OuterMessage"]
            .nested_messages["InterMessage"]
            .source_code_line,
            7,
        )
        self.assertEqual(
            file_set.messages_map["OuterMessage"]
            .nested_enums["InterEnum"]
            .source_code_line,
            8,
        )
        self.assertEqual(
            file_set.messages_map["OuterMessage"]
            .nested_enums["InterEnum"]
            .values[2]
            .source_code_line,
            10,
        )

    def test_file_set_packaging_options(self):
        option1 = descriptor_pb2.FileOptions()
        option1.java_package = "com.google.example.v1"
        option1.php_namespace = "Google\\Cloud\\Example\\V1"
        option1.java_outer_classname = "Foo"
        option2 = descriptor_pb2.FileOptions()
        option2.java_outer_classname = "Bar"
        # Two proto files have the same packging options.
        file1 = make_file_pb2(name="proto1", options=option1)
        file2 = make_file_pb2(name="proto2", options=option2)
        file_set = make_file_set(files=[file1, file2])
        self.assertTrue(file_set.packaging_options_map)

        self.assertEqual(
            list(file_set.packaging_options_map["java_package"].keys()),
            ["com.google.example.v1"],
        )
        self.assertEqual(
            list(file_set.packaging_options_map["php_namespace"].keys()),
            ["Google\\Cloud\\Example\\V1"],
        )
        self.assertEqual(
            list(file_set.packaging_options_map["java_outer_classname"].keys()),
            ["Foo", "Bar"],
        )

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


if __name__ == "__main__":
    unittest.main()

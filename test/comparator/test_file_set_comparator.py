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
    make_service,
    make_method,
    make_file_set,
    make_file_pb2,
    make_message,
    make_field,
    make_enum,
)
from src.comparator.file_set_comparator import FileSetComparator
from src.findings.finding_container import FindingContainer
from google.protobuf import descriptor_pb2
from google.api import resource_pb2


class FileSetComparatorTest(unittest.TestCase):
    def tearDown(self):
        FindingContainer.reset()

    def test_service_change(self):
        service_original = make_service(methods=(make_method(name="DoThing"),))
        service_update = make_service()
        FileSetComparator(
            make_file_set(files=[make_file_pb2(services=[service_original])]),
            make_file_set(files=[make_file_pb2(services=[service_update])]),
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map["An rpc method DoThing is removed"]
        self.assertEqual(finding.category.name, "METHOD_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "my_proto.proto")

    def test_message_change(self):
        message_original = make_message(
            fields=(make_field(name="field_one", number=1),)
        )
        message_update = make_message(fields=(make_field(name="field_two", number=1),))
        FileSetComparator(
            make_file_set(files=[make_file_pb2(messages=[message_original])]),
            make_file_set(files=[make_file_pb2(messages=[message_update])]),
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "Name of an existing field is changed from `field_one` to `field_two`."
        ]
        self.assertEqual(finding.category.name, "FIELD_NAME_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "my_proto.proto")

    def test_enum_change(self):
        enum_original = make_enum(
            name="Irrelevant",
            values=(
                ("RED", 1),
                ("GREEN", 2),
                ("BLUE", 3),
            ),
        )
        enum_update = make_enum(
            name="Irrelevant",
            values=(
                ("RED", 1),
                ("GREEN", 2),
            ),
        )
        FileSetComparator(
            make_file_set(files=[make_file_pb2(enums=[enum_original])]),
            make_file_set(files=[make_file_pb2(enums=[enum_update])]),
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map["An EnumValue BLUE is removed"]
        self.assertEqual(finding.category.name, "ENUM_VALUE_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "my_proto.proto")

    def test_resources_existing_pattern_change(self):
        options_original = descriptor_pb2.FileOptions()
        options_original.Extensions[resource_pb2.resource_definition].append(
            resource_pb2.ResourceDescriptor(
                type=".example.v1.Bar",
                pattern=[
                    "foo/{foo}/bar/{bar}",
                ],
            )
        )
        file_pb2 = make_file_pb2(
            name="foo.proto", package=".example.v1", options=options_original
        )
        file_set_original = make_file_set(files=[file_pb2])
        options_update = descriptor_pb2.FileOptions()
        options_update.Extensions[resource_pb2.resource_definition].append(
            resource_pb2.ResourceDescriptor(
                type=".example.v1.Bar",
                pattern=["foo/{foo}/bar/"],
            )
        )
        file_pb2 = make_file_pb2(
            name="foo.proto", package=".example.v1", options=options_update
        )
        file_set_update = make_file_set(files=[file_pb2])

        FileSetComparator(file_set_original, file_set_update).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        file_resource_pattern_change = findings_map[
            "Pattern value of the resource definition '.example.v1.Bar' is updated from 'foo/{foo}/bar/{bar}' to 'foo/{foo}/bar/'."
        ]
        self.assertEqual(
            file_resource_pattern_change.category.name, "RESOURCE_DEFINITION_CHANGE"
        )
        self.assertEqual(
            file_resource_pattern_change.location.proto_file_name,
            "foo.proto",
        )

    def test_resources_addition(self):
        file_set_original = make_file_set(
            files=[make_file_pb2(name="foo.proto", package=".example.v1")]
        )

        options_update = descriptor_pb2.FileOptions()
        options_update.Extensions[resource_pb2.resource_definition].append(
            resource_pb2.ResourceDescriptor(
                type=".example.v1.Bar",
                pattern=["foo/{foo}/bar/{bar}"],
            )
        )
        file_pb2 = make_file_pb2(
            name="foo.proto", package=".example.v1", options=options_update
        )
        file_set_update = make_file_set(files=[file_pb2])
        FileSetComparator(file_set_original, file_set_update).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        file_resource_addition = findings_map[
            "A file-level resource definition '.example.v1.Bar' has been added."
        ]
        self.assertEqual(
            file_resource_addition.category.name,
            "RESOURCE_DEFINITION_ADDITION",
        )
        self.assertEqual(
            file_resource_addition.location.proto_file_name,
            "foo.proto",
        )

    def test_packaging_options_change(self):
        file_options_original = descriptor_pb2.FileOptions()
        file_options_original.php_namespace = "example_php_namespace"
        file_original = make_file_pb2(
            name="original.proto", options=file_options_original
        )

        file_options_update = descriptor_pb2.FileOptions()
        file_options_update.php_namespace = "example_php_namespace_update"
        file_update = make_file_pb2(name="update.proto", options=file_options_update)

        FileSetComparator(
            make_file_set(files=[file_original]),
            make_file_set(files=[file_update]),
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        go_package_option_removal = findings_map[
            "An exisiting packaging option for php_namespace is removed."
        ]
        self.assertEqual(
            go_package_option_removal.category.name, "PACKAGING_OPTION_REMOVAL"
        )

        ruby_package_option_removal = findings_map[
            "An exisiting packaging option for php_namespace is added."
        ]
        self.assertEqual(
            ruby_package_option_removal.category.name, "PACKAGING_OPTION_ADDITION"
        )


if __name__ == "__main__":
    unittest.main()

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
from test.tools.mock_resources import (
    make_resource_descriptor,
    make_resource_database,
    make_field_annotation_resource_reference,
)
from src.comparator.field_comparator import FieldComparator
from src.findings.finding_container import FindingContainer
from src.comparator.resource_database import ResourceDatabase
from google.protobuf import descriptor_pb2 as desc
from google.api import resource_pb2


class FieldComparatorTest(unittest.TestCase):
    def setUp(self):
        self.finding_container = FindingContainer()

    def test_field_removal(self):
        field_foo = make_field("Foo")
        FieldComparator(field_foo, None, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "An existing field `Foo` is removed.")
        self.assertEqual(finding.category.name, "FIELD_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_field_addition(self):
        field_foo = make_field("Foo")
        FieldComparator(None, field_foo, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "A new field `Foo` is added.")
        self.assertEqual(finding.category.name, "FIELD_ADDITION")

    def test_name_change(self):
        field_foo = make_field("Foo")
        field_bar = make_field("Bar")
        FieldComparator(field_foo, field_bar, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Name of an existing field is changed from `Foo` to `Bar`.",
        )
        self.assertEqual(finding.category.name, "FIELD_NAME_CHANGE")

    def test_repeated_label_change(self):
        field_repeated = make_field(repeated=True)
        field_non_repeated = make_field(repeated=False)
        FieldComparator(
            field_repeated, field_non_repeated, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Repeated state of an existing field `my_field` is changed.",
        )
        self.assertEqual(finding.category.name, "FIELD_REPEATED_CHANGE")

    def test_field_behavior_change(self):
        field_required = make_field(required=True)
        field_non_required = make_field(required=False)
        # Required to optional, non-breaking change.
        FieldComparator(
            field_required, field_non_required, self.finding_container
        ).compare()
        findings = self.finding_container.getAllFindings()
        self.assertFalse(findings)
        # Required to optional, non-breaking change.
        FieldComparator(
            field_non_required, field_required, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Field behavior of an existing field `my_field` is changed.",
        )
        self.assertEqual(finding.category.name, "FIELD_BEHAVIOR_CHANGE")

    def test_primitive_type_change(self):
        field_int = make_field(proto_type="TYPE_INT32")
        field_string = make_field(proto_type="TYPE_STRING")
        FieldComparator(field_int, field_string, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of an existing field `my_field` is changed from `int32` to `string`.",
        )
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")

    def test_message_type_change(self):
        field_message = make_field(type_name=".example.v1.Enum")
        field_message_update = make_field(type_name=".example.v1beta1.EnumUpdate")
        FieldComparator(
            field_message, field_message_update, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of an existing field `my_field` is changed from `.example.v1.Enum` to `.example.v1beta1.EnumUpdate`.",
        )
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")

    def test_message_type_change_minor_version_update(self):
        field_message = make_field(type_name=".example.v1.Enum", api_version="v1")
        field_message_update = make_field(
            type_name=".example.v1beta1.Enum", api_version="v1beta1"
        )
        FieldComparator(
            field_message, field_message_update, self.finding_container
        ).compare()
        findings = self.finding_container.getAllFindings()
        self.assertFalse(findings)

    def test_type_change_map_entry1(self):
        # Existing field is message_type, while the update field type is map. Breaking change.
        # Normally it will catch by type_name comparison. But in case we have a
        # message name as `{FieldName}Entry` which is the same as auto-generated nested message name,
        # we still consider the condition that the type of an existing field is changed from
        # normal message (`{FieldName}Entry`) to map entry message (`{FieldName}Entry`).
        field_no_map = make_field(
            proto_type="TYPE_MESSAGE", type_name=".exmaple.MapEntry"
        )
        # [Constructing] map<string, string> field
        key_field = make_field(proto_type="TYPE_STRING", number=1)
        value_field = make_field(proto_type="TYPE_STRING", number=2)
        field_map = make_field(
            proto_type="TYPE_MESSAGE",
            type_name=".exmaple.MapEntry",
            map_entry={"key": key_field, "value": value_field},
        )
        FieldComparator(field_no_map, field_map, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of an existing field `my_field` is changed from `.exmaple.MapEntry` to a map.",
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_type_change_map_entry2(self):
        # Existing field type is a map, while the update field type is a normal message. Breaking change.
        # Normally it will catch by type_name comparison. But in case we have a
        # message name as `{FieldName}Entry` which is the same as auto-generated nested message name,
        # we still consider the condition that the type of an existing field is changed from
        # map entry message (`{FieldName}Entry`) to normal message (`{FieldName}Entry`).
        field_no_map = make_field(
            proto_type="TYPE_MESSAGE", type_name=".exmaple.MapEntry"
        )
        # [Constructing] map<string, string> field
        key_field = make_field(proto_type="TYPE_STRING", number=1)
        value_field = make_field(proto_type="TYPE_STRING", number=2)
        field_map = make_field(
            proto_type="TYPE_MESSAGE",
            type_name=".exmaple.MapEntry",
            map_entry={"key": key_field, "value": value_field},
        )
        FieldComparator(field_map, field_no_map, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of an existing field `my_field` is changed from a map to `.exmaple.MapEntry`.",
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_type_change_map_entry3(self):
        # Both fields are map type. But the key, value types are not identical. Breaking change.
        # [Constructing] map<string, string> field
        key_original = make_field(proto_type="TYPE_STRING", number=1)
        value_original = make_field(proto_type="TYPE_STRING", number=2)
        field_original = make_field(
            proto_type="TYPE_MESSAGE",
            type_name=".exmaple.MapEntry",
            map_entry={"key": key_original, "value": value_original},
        )
        # [Constructing] map<key, value> field
        key_update = make_field(
            proto_type="TYPE_MESSAGE", number=1, type_name=".example.key"
        )
        value_update = make_field(
            proto_type="TYPE_MESSAGE", number=2, type_name=".example.value"
        )
        field_update = make_field(
            proto_type="TYPE_MESSAGE",
            type_name=".exmaple.MapEntry",
            map_entry={"key": key_update, "value": value_update},
        )

        FieldComparator(field_original, field_update, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Type of an existing field `my_field` is changed from `map<string, string>` to `map<.example.key, .example.value>`.",
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.category.name, "FIELD_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_type_change_map_entry4(self):
        # Both fields are map type. But the key, value types are not identical.
        # But only the versions pare are different. Non-breaking change.
        # [Constructing] map<string, .example.v1.value> field
        key_original = make_field(proto_type="TYPE_STRING", number=1)
        value_original = make_field(
            proto_type="TYPE_MESSAGE", type_name=".example.v1.value", number=2
        )
        field_original = make_field(
            proto_type="TYPE_MESSAGE",
            type_name=".exmaple.MapEntry",
            map_entry={"key": key_original, "value": value_original},
            api_version="v1",
        )
        # [Constructing] map<string, .example.v1beta1.value> field
        key_update = make_field(proto_type="TYPE_STRING", number=1)
        value_update = make_field(
            proto_type="TYPE_MESSAGE", number=2, type_name=".example.v1beta1.value"
        )
        field_update = make_field(
            proto_type="TYPE_MESSAGE",
            type_name=".exmaple.MapEntry",
            map_entry={"key": key_update, "value": value_update},
            api_version="v1beta1",
        )

        FieldComparator(field_original, field_update, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()
        self.assertFalse(finding)

    def test_out_oneof(self):
        field_oneof = make_field(name="Foo", oneof_index=0, oneof_name="oneof_field")
        field_not_oneof = make_field(name="Foo")
        FieldComparator(field_oneof, field_not_oneof, self.finding_container).compare()
        findings = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings["An existing field `Foo` is moved out of One-of."]
        self.assertEqual(finding.category.name, "FIELD_ONEOF_MOVE_OUT")

    def test_into_oneof(self):
        field_oneof = make_field(name="Foo", oneof_index=0, oneof_name="oneof_field")
        field_not_oneof = make_field(name="Foo")
        FieldComparator(field_not_oneof, field_oneof, self.finding_container).compare()
        findings = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings["An existing field `Foo` is moved into One-of."]
        self.assertEqual(finding.category.name, "FIELD_ONEOF_MOVE_IN")

    def test_proto3_optional_change(self):
        field_optional = make_field(
            name="Foo", oneof_index=0, oneof_name="oneof_field", proto3_optional=True
        )
        field_not_optional = make_field(
            name="Foo", oneof_index=0, oneof_name="oneof_field"
        )
        FieldComparator(
            field_optional, field_not_optional, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "Proto3 optional state of an existing field `Foo` is changed to required.",
        )
        self.assertEqual(finding.category.name, "FIELD_PROTO3_OPTIONAL_CHANGE")

    def test_resource_reference_addition_breaking(self):
        # The added resource reference is not in the database. Breaking change.
        # The original field is without resource reference.
        field_without_reference = make_field(name="Test")
        # The update field has resource reference, but it does not exist
        # in the global database.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference = make_field(name="Test", options=field_options)
        FieldComparator(
            field_without_reference, field_with_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getActionableFindings()[0]
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_ADDITION")
        self.assertEqual(
            finding.message,
            "A resource reference option is added to the field `Test`, but it is not defined anywhere",
        )

    def test_resource_reference_type_addition_non_breaking(self):
        # The added resource reference is in the database. Non-breaking change.
        # The original field is without resource reference.
        field_without_reference = make_field(name="Test")
        # Create a database with resource `example.v1/Foo` registered.
        resource = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["foo/{foo}"]
        )
        resource_database = make_resource_database(resources=[resource])
        # The update field has resource reference of type `example.v1/Foo`.
        field_options = desc.FieldOptions()
        field_options.Extensions[
            resource_pb2.resource_reference
        ].type = "example.v1/Foo"
        field_with_reference = make_field(
            name="Test", options=field_options, resource_database=resource_database
        )
        FieldComparator(
            field_without_reference, field_with_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message, "A resource reference option is added to the field `Test`."
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")

    def test_resource_reference_child_type_addition_non_breaking(self):
        # The added resource reference is in the database. Non-breaking change.
        # The original field is without resource reference.
        field_without_reference = make_field(name="Test")
        # Create a database with resource `example.v1/Foo` registered.
        resource = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["foo/{foo}"]
        )
        resource_child = make_resource_descriptor(
            resource_type="example.v1/Bar",
            resource_patterns=["foo/{foo}/bar/{bar}"],
        )
        resource_database = make_resource_database(resources=[resource, resource_child])
        # The update field has resource reference of child_type `example.v1/Bar`.
        field_options = desc.FieldOptions()
        field_options.Extensions[
            resource_pb2.resource_reference
        ].child_type = "example.v1/Bar"
        field_with_reference = make_field(
            name="Test", options=field_options, resource_database=resource_database
        )
        FieldComparator(
            field_without_reference, field_with_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message, "A resource reference option is added to the field `Test`."
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")

    def test_resource_reference_removal_breaking1(self):
        # Removed resource reference is not added in message options. Breaking.
        # Original field has resource reference `example.v1/Foo`.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference = make_field(name="Test", options=field_options)
        # The update field has no resource reference, and no resource reference is
        # defined in the messasge.
        field_without_reference = make_field(name="Test")
        FieldComparator(
            field_with_reference, field_without_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getActionableFindings()[0]
        self.assertEqual(
            finding.message,
            "A resource reference option of the field `Test` is removed.",
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")

    def test_resource_reference_removal_breaking2(self):
        # Removed resource reference is defined by type, which is not identical
        # with the message options.
        # Original field has resource reference `example.v1/Foo`.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference = make_field(name="Test", options=field_options)
        # Update field has no resource reference, and the resource type
        # is different from the message options type.
        message_resource = make_resource_descriptor(
            resource_type="NotInteresting", resource_patterns=["NotInteresting"]
        )
        field_without_reference = make_field(
            name="Test", message_resource=message_resource
        )
        FieldComparator(
            field_with_reference, field_without_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getActionableFindings()[0]
        self.assertEqual(
            finding.message,
            "A resource reference option of the field `Test` is removed.",
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")

    def test_resource_reference_removal_breaking3(self):
        # Removed resource reference is defined by child type, which can not
        # be resolved to identical resource with the message options.
        # Original field has resource reference `example.v1/Foo`.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=True
        )
        field_with_reference = make_field(name="Test", options=field_options)
        # Update field has no resource reference, and the removed resource child type
        # is not identical with the message resource option.
        message_resource = make_resource_descriptor(
            resource_type="example.v1/Bar", resource_patterns=["bar/{bar}"]
        )
        field_resource = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["foo/{foo}"]
        )
        # Register the two resources in the database.
        resource_database = make_resource_database(
            resources=[message_resource, field_resource]
        )

        field_without_reference = make_field(
            name="Test",
            resource_database=resource_database,
            message_resource=message_resource,
        )
        FieldComparator(
            field_with_reference, field_without_reference, self.finding_container
        ).compare()
        # `bar/{bar}` is not parent resource of `foo/{foo}`.
        finding = self.finding_container.getActionableFindings()[0]
        self.assertEqual(
            finding.message,
            "A resource reference option of the field `Test` is removed.",
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")

    def test_resource_reference_removal_non_breaking1(self):
        # Removed resource reference is defined by type, and it is
        # added back to the message options.
        # Original field has resource reference `example.v1/Foo`.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference = make_field(name="Test", options=field_options)
        # Update field has no resource reference. But the message has
        # resource options `example.v1/Foo`.
        message_resource = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["bar/{bar}"]
        )

        field_without_reference = make_field(
            name="Test", message_resource=message_resource
        )
        FieldComparator(
            field_with_reference, field_without_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "A resource reference option of the field `Test` is removed, but added back to the message options.",
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MINOR")

    def test_resource_reference_removal_non_breaking2(self):
        # Removed resource reference is defined by child type, and it
        # can be resolved to the same resource with the message options.
        # Original field has resource reference `example.v1/Foo`.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference = make_field(name="Test", options=field_options)
        # Update field has no resource reference. But the message has
        # resource options `example.v1/Foo`.
        message_resource = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["bar/{bar}"]
        )
        field_resource = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["bar/{bar}/foo/{foo}"]
        )
        # Register the two resources in the database.
        resource_database = make_resource_database(
            resources=[message_resource, field_resource]
        )
        field_without_reference = make_field(
            name="Test",
            message_resource=message_resource,
            resource_database=resource_database,
        )
        # `bar/{bar}` is the parent resource of `bar/{bar}/foo/{foo}`.
        FieldComparator(
            field_with_reference, field_without_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(
            finding.message,
            "A resource reference option of the field `Test` is removed, but added back to the message options.",
        )
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_REMOVAL")
        self.assertEqual(finding.change_type.name, "MINOR")

    def test_resource_reference_change_same_type(self):
        # The field has the identical resource reference.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference = make_field(name="Test", options=field_options)
        FieldComparator(
            field_with_reference, field_with_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()
        # No breaking change should be detected.
        self.assertFalse(finding)

    def test_resource_reference_change_same_child_type(self):
        # The field has the identical resource reference.
        field_options = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=True
        )
        field_with_reference = make_field(name="Test", options=field_options)
        FieldComparator(
            field_with_reference, field_with_reference, self.finding_container
        ).compare()
        finding = self.finding_container.getAllFindings()
        # No breaking change should be detected.
        self.assertFalse(finding)

    def test_resource_reference_change_type_conversion_non_breaking(self):
        child_resource = make_resource_descriptor(
            resource_type="example.v1/Foo",
            resource_patterns=["bar/{bar}/foo/{foo}", "bar/{bar}/foo"],
        )
        parent_resource = make_resource_descriptor(
            resource_type="example.v1/Bar", resource_patterns=["bar/{bar}"]
        )
        # Register two resources in database.
        resource_database = make_resource_database(
            resources=[child_resource, parent_resource]
        )
        # The original field is defined by child type.
        field_options_child = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=True
        )
        field_with_reference_child = make_field(
            name="Test",
            options=field_options_child,
            resource_database=resource_database,
        )

        # The update field is defined by parent type.
        field_options_parent = make_field_annotation_resource_reference(
            resource_type="example.v1/Bar", is_child_type=False
        )
        field_with_reference_parent = make_field(
            name="Test",
            options=field_options_parent,
            resource_database=resource_database,
        )
        # The two resources can be resolved to the identical resource.
        FieldComparator(
            field_with_reference_child,
            field_with_reference_parent,
            self.finding_container,
        ).compare()
        finding = self.finding_container.getAllFindings()
        # No breaking change should be detected.
        self.assertFalse(finding)

        # Reverse should be same since the two resources can
        # be resolved to the identical resource.
        FieldComparator(
            field_with_reference_parent,
            field_with_reference_child,
            self.finding_container,
        ).compare()
        finding = self.finding_container.getAllFindings()
        # No breaking change should be detected.
        self.assertFalse(finding)

    def test_resource_reference_change_type_conversion_breaking(self):
        resource_bar = make_resource_descriptor(
            resource_type="example.v1/Bar",
            resource_patterns=["bar/{bar}/foo/{foo}", "bar/{bar}/foo"],
        )
        resource_foo = make_resource_descriptor(
            resource_type="example.v1/Foo", resource_patterns=["foo/{foo}"]
        )
        # Register two resources in database.
        resource_database = make_resource_database(
            resources=[resource_bar, resource_foo]
        )
        # The original field is defined by child type.
        field_options_child = make_field_annotation_resource_reference(
            resource_type="example.v1/Bar", is_child_type=True
        )
        field_with_reference_child = make_field(
            name="Test",
            options=field_options_child,
            resource_database=resource_database,
        )

        # The update field is defined by parent type.
        field_options_parent = make_field_annotation_resource_reference(
            resource_type="example.v1/Foo", is_child_type=False
        )
        field_with_reference_parent = make_field(
            name="Test",
            options=field_options_parent,
            resource_database=resource_database,
        )
        # The two resources can nnot be resolved to the identical resource.
        FieldComparator(
            field_with_reference_child,
            field_with_reference_parent,
            self.finding_container,
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "RESOURCE_REFERENCE_CHANGE")
        self.assertEqual(
            finding.message,
            "The child_type `example.v1/Bar` and type `example.v1/Foo` of resource reference option in field `Test` cannot be resolved to the identical resource.",
        )
        self.assertEqual(finding.change_type.name, "MAJOR")


if __name__ == "__main__":
    unittest.main()

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

from proto_bcd.findings.finding_container import FindingContainer
from proto_bcd.findings.finding_category import (
    FindingCategory,
    ConventionalCommitTag,
)
from proto_bcd.comparator.wrappers import Field
from proto_bcd.comparator.wrappers import FORMAT_UNSPECIFIED


class FieldComparator:
    # resource_database: global resource database that contains all file-level resource definitions
    #                    and message-level resource options.
    # message_resource: message-level resource definition.
    # We need the resource database information to determine if the resource_reference
    # annotation removal or change is breaking or not.
    def __init__(
        self,
        field_original: Field,
        field_update: Field,
        finding_container: FindingContainer,
        context: str,
    ):
        self.field_original = field_original
        self.field_update = field_update
        self.finding_container = finding_container
        self.context = context

    def compare(self):
        # 1. If original FieldDescriptor is None, then a
        # new FieldDescriptor is added.
        if self.field_original is None:
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_ADDITION,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.source_code_line,
                subject=self.field_update.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FEAT,
            )
            return

        # 2. If updated FieldDescriptor is None, then
        # the original FieldDescriptor is removed.
        if self.field_update is None:
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_REMOVAL,
                proto_file_name=self.field_original.proto_file_name,
                source_code_line=self.field_original.source_code_line,
                subject=self.field_original.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
            )
            return

        # 3. If both FieldDescriptors are existing, check
        # if the name is changed.
        if self.field_original.name != self.field_update.name:
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_NAME_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.source_code_line,
                oldsubject=self.field_original.name,
                subject=self.field_update.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_original.nested_path,
            )
            return

        # 4. If the FieldDescriptors have the same name, check if the
        # repeated state of them stay the same.
        if self.field_original.repeated.value != self.field_update.repeated.value:
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_REPEATED_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.repeated.source_code_line,
                subject=self.field_update.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_update.nested_path,
            )
        # Field option change from optional to required is breaking.
        if not self.field_original.required.value and self.field_update.required.value:
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_BEHAVIOR_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.required.source_code_line,
                subject=self.field_update.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_update.nested_path
                + ["(google.api.field_behavior)"],
            )
        # 5. Check the type of the field.
        if self.field_original.proto_type.value != self.field_update.proto_type.value:
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_TYPE_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.proto_type.source_code_line,
                subject=self.field_update.name,
                context=self.context,
                oldtype=self.field_original.proto_type.value,
                type=self.field_update.proto_type.value,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_update.nested_path,
            )
        # If field has the same primitive type, then the type should be identical.
        # If field has the same non-primitive type like `TYPE_ENUM`.
        # Check the type_name of the field.
        elif self.field_original.type_name and (
            self.field_original.type_name.value != self.field_update.type_name.value
        ):
            # Version update is allowed here, for example from `.example.v1.Enum` to `.example.v1beta1.Enum`.
            # But from `.example.v1.Enum` to `.example.v2.EnumUpdate` is breaking.
            transformed_type_name = self._transformed_type_name(
                self.field_original.type_name.value
            )
            if (
                not transformed_type_name
                or transformed_type_name != self.field_update.type_name.value
            ):
                self.finding_container.add_finding(
                    category=FindingCategory.FIELD_TYPE_CHANGE,
                    proto_file_name=self.field_update.proto_file_name,
                    source_code_line=self.field_update.type_name.source_code_line,
                    subject=self.field_original.name,
                    context=self.context,
                    oldtype=self.field_original.type_name.value,
                    type=self.field_update.type_name.value,
                    conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                    extra_info=self.field_update.nested_path,
                )
        # If the fields have the same type_name, but they are map type,
        # the key type and value type should also be identical.
        elif self.field_original.type_name:
            if self.field_original.is_map_type and not self.field_update.is_map_type:
                key_original = self.field_original.map_entry_type["key"]
                value_original = self.field_original.map_entry_type["value"]
                self.finding_container.add_finding(
                    category=FindingCategory.FIELD_TYPE_CHANGE,
                    proto_file_name=self.field_update.proto_file_name,
                    source_code_line=self.field_update.type_name.source_code_line,
                    subject=self.field_original.name,
                    context=self.context,
                    oldtype=f"map<{key_original}, {value_original}>",
                    type=self.field_update.type_name.value,
                    conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                    extra_info=self.field_update.nested_path,
                )
            elif not self.field_original.is_map_type and self.field_update.is_map_type:
                key_update = self.field_update.map_entry_type["key"]
                value_update = self.field_update.map_entry_type["value"]
                self.finding_container.add_finding(
                    category=FindingCategory.FIELD_TYPE_CHANGE,
                    proto_file_name=self.field_update.proto_file_name,
                    source_code_line=self.field_update.type_name.source_code_line,
                    subject=self.field_original.name,
                    context=self.context,
                    oldtype=self.field_original.type_name.value,
                    type=f"map<{key_update}, {value_update}>",
                    conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                    extra_info=self.field_update.nested_path,
                )
            # Both fields are map types, compare the key and value type.
            elif self.field_original.is_map_type and self.field_update.is_map_type:
                key_original = self.field_original.map_entry_type["key"]
                value_original = self.field_original.map_entry_type["value"]
                key_update = self.field_update.map_entry_type["key"]
                value_update = self.field_update.map_entry_type["value"]
                # If either the key, value is not primitive type, then it should allow
                # minor version updates.
                identical_key_type = (
                    key_original == key_update
                    or self._transformed_type_name(key_original) == key_update
                )
                identical_value_type = (
                    value_original == value_update
                    or self._transformed_type_name(value_original) == value_update
                )
                if not (identical_key_type and identical_value_type):
                    self.finding_container.add_finding(
                        category=FindingCategory.FIELD_TYPE_CHANGE,
                        proto_file_name=self.field_update.proto_file_name,
                        source_code_line=self.field_update.type_name.source_code_line,
                        subject=self.field_original.name,
                        context=self.context,
                        oldtype=f"map<{key_original}, {value_original}>",
                        type=f"map<{key_update}, {value_update}>",
                        conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                        extra_info=self.field_update.nested_path,
                    )

        # 6. Check the oneof state of the field.
        if self.field_original.oneof != self.field_update.oneof:
            proto_file_name = self.field_update.proto_file_name
            source_code_line = self.field_update.source_code_line
            if self.field_original.oneof:
                self.finding_container.add_finding(
                    category=FindingCategory.FIELD_ONEOF_MOVE_OUT,
                    proto_file_name=proto_file_name,
                    source_code_line=source_code_line,
                    subject=self.field_original.name,
                    context=self.context,
                    conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                    extra_info=self.field_update.nested_path,
                )
            else:
                if self.field_update.proto3_optional:
                    # Optional primitive fields are implemented as single member
                    # oneofs. In this case, we treat it as just a change in
                    # `optional` option.
                    self.finding_container.add_finding(
                        category=FindingCategory.FIELD_PROTO3_OPTIONAL_CHANGE,
                        proto_file_name=proto_file_name,
                        source_code_line=source_code_line,
                        subject=self.field_original.name,
                        context=self.context,
                        conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                        extra_info=self.field_update.nested_path,
                    )
                else:
                    self.finding_container.add_finding(
                        category=FindingCategory.FIELD_ONEOF_MOVE_IN,
                        proto_file_name=proto_file_name,
                        source_code_line=source_code_line,
                        subject=self.field_original.name,
                        context=self.context,
                        conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                        extra_info=self.field_update.nested_path,
                    )
        # 7. Check the proto3_optional state of the field.
        elif (
            self.field_original.oneof
            and self.field_original.proto3_optional != self.field_update.proto3_optional
        ):
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_PROTO3_OPTIONAL_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.source_code_line,
                subject=self.field_original.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_update.nested_path,
            )

        # 8. Check `google.api.resource_reference` annotation.
        self._compare_resource_reference()

        # 9. Field changing a field format is breaking.
        if (
            self.field_original.valueFormat.value != FORMAT_UNSPECIFIED
            and self.field_original.valueFormat.value
            != self.field_update.valueFormat.value
        ):
            self.finding_container.add_finding(
                category=FindingCategory.FIELD_FORMAT_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.required.source_code_line,
                subject=self.field_update.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_update.nested_path
                + ["(google.api.field_info).format"],
            )

    def _compare_resource_reference(self):
        field_original = self.field_original
        field_update = self.field_update
        resource_ref_original = field_original.resource_reference
        resource_ref_update = field_update.resource_reference
        # No resource_reference annotations found for the field in both versions.
        if not resource_ref_original and not resource_ref_update:
            return
        # A `google.api.resource_reference` annotation is added.
        if not resource_ref_original and resource_ref_update:
            self.finding_container.add_finding(
                category=FindingCategory.RESOURCE_REFERENCE_ADDITION,
                proto_file_name=field_update.proto_file_name,
                source_code_line=resource_ref_update.source_code_line,
                subject=field_original.name,
                context=self.context,
                conventional_commit_tag=ConventionalCommitTag.FEAT,
                extra_info=self.field_update.nested_path
                + ["(google.api.resource_reference)"],
            )
            return
        # Resource annotation is removed, check if it is added as a message resource.
        if resource_ref_original and not resource_ref_update:
            if not self._resource_ref_in_local(resource_ref_original.value):
                self.finding_container.add_finding(
                    category=FindingCategory.RESOURCE_REFERENCE_REMOVAL,
                    proto_file_name=field_original.proto_file_name,
                    source_code_line=resource_ref_original.source_code_line,
                    subject=field_original.name,
                    context=self.context,
                    conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                )
            else:
                # TODO(@alexander-fenster): this looks suspicious, need to write tests and provide the correct message
                self.finding_container.add_finding(
                    category=FindingCategory.RESOURCE_REFERENCE_MOVED,
                    proto_file_name=field_original.proto_file_name,
                    source_code_line=resource_ref_original.source_code_line,
                    subject=field_original.name,
                    context=self.context,
                    conventional_commit_tag=ConventionalCommitTag.FEAT,
                )
            return
        # Resource annotation is both existing in the field for original and update versions.
        # They both use `type` or `child_type`.
        if field_original.child_type == field_update.child_type:
            original_type = (
                resource_ref_original.value.type
                or resource_ref_original.value.child_type
            )
            update_type = (
                resource_ref_update.value.type or resource_ref_update.value.child_type
            )
            if original_type != update_type:
                self.finding_container.add_finding(
                    category=FindingCategory.RESOURCE_REFERENCE_CHANGE,
                    proto_file_name=field_update.proto_file_name,
                    source_code_line=resource_ref_update.source_code_line,
                    subject=field_original.name,
                    context=self.context,
                    oldtype=original_type,
                    type=update_type,
                    conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                    extra_info=self.field_update.nested_path
                    + ["(google.api.resource_reference)", f"{update_type}"],
                )
            return
        # The `type` is changed to `child_type` or `child_type` is changed to `type`, but
        # resulting referenced resource patterns can be resolved to be identical,
        # in that case it is not considered breaking.
        # Register the message-level resource into the global resource database,
        # so that we can query the parent resources for child_type.
        if field_original.child_type:
            self._is_parent_type(
                resource_ref_original.value.child_type,
                resource_ref_update.value.type,
                True,
                resource_ref_update.source_code_line,
            )
        if field_update.child_type:
            self._is_parent_type(
                resource_ref_update.value.child_type,
                resource_ref_original.value.type,
                False,
                resource_ref_update.source_code_line,
            )

    def _transformed_type_name(self, type_name):
        # Tranform type name to allow minor version update.
        # For example from `.example.v1.Enum` to `.example.v1beta1.Enum`.
        # But from `.example.v1.Enum` to `.example.v2.EnumUpdate` is breaking.
        api_version_original = self.field_original.api_version
        api_version_update = self.field_update.api_version
        transformed_type_name = (
            type_name.replace(api_version_original, api_version_update)
            if api_version_original
            else None
        )
        return transformed_type_name

    def _resource_in_database(self, resource_ref) -> bool:
        # Check whether the added resource reference is in the database.
        rb_update = self.field_update.resource_database
        if not rb_update:
            return False
        resources = (
            rb_update.get_parent_resources_by_child_type(resource_ref.value.child_type)
            if self.field_update.child_type
            else rb_update.get_resource_by_type(resource_ref.value.type)
        )
        return bool(resources)

    def _resource_ref_in_local(self, resource_ref):
        """Check if the resource type is in the local resources defined by a message option."""
        mr_update = self.field_update.message_resource
        if not mr_update:
            return False
        checked_type = resource_ref.type or resource_ref.child_type
        if not checked_type:
            raise TypeError(
                "In a resource_reference annotation, either `type` or `child_type` field should be defined"
            )
        if self.field_original.child_type:
            rb_update = self.field_update.resource_database
            parent_resources = rb_update.get_parent_resources_by_child_type(
                resource_ref.child_type
            )
            if not any(
                mr_update.value.type == resource.value.type
                for resource in parent_resources
            ):
                return False
        elif mr_update.value.type != resource_ref.type:
            return False
        return True

    def _is_parent_type(
        self, child_type, parent_type, original_is_child, source_code_line
    ):
        if original_is_child:
            rb_original = self.field_original.resource_database
            parent_resources = rb_original.get_parent_resources_by_child_type(
                child_type
            )
        else:
            rb_update = self.field_update.resource_database
            parent_resources = rb_update.get_parent_resources_by_child_type(child_type)
        if not any(parent.value.type == parent_type for parent in parent_resources):
            # Resulting referenced resource patterns cannot be resolved identical.
            self.finding_container.add_finding(
                category=FindingCategory.RESOURCE_REFERENCE_CHANGE_CHILD_TYPE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=source_code_line,
                subject=self.field_original.name,
                context=self.context,
                oldtype=child_type,
                type=parent_type,
                conventional_commit_tag=ConventionalCommitTag.FIX_BREAKING,
                extra_info=self.field_update.nested_path
                + ["(google.api.resource_reference)"],
            )

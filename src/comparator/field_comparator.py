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

from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory
from src.comparator.wrappers import Field


class FieldComparator:
    # global_resources: file-level resource definitions.
    # local_resource: message-level resource definition.
    # We need the resource database information to determine if the resource_reference
    # annotation removal or change is breaking or not.
    def __init__(
        self,
        field_original: Field,
        field_update: Field,
        finding_container: FindingContainer,
    ):
        self.field_original = field_original
        self.field_update = field_update
        self.finding_container = finding_container

    def compare(self):
        # 1. If original FieldDescriptor is None, then a
        # new FieldDescriptor is added.
        if self.field_original is None:
            self.finding_container.addFinding(
                category=FindingCategory.FIELD_ADDITION,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.source_code_line,
                message=f"A new field `{self.field_update.name}` is added.",
                actionable=False,
            )
            return

        # 2. If updated FieldDescriptor is None, then
        # the original FieldDescriptor is removed.
        if self.field_update is None:
            self.finding_container.addFinding(
                category=FindingCategory.FIELD_REMOVAL,
                proto_file_name=self.field_original.proto_file_name,
                source_code_line=self.field_original.source_code_line,
                message=f"An existing field `{self.field_original.name}` is removed.",
                actionable=True,
            )
            return

        self.global_resources_original = self.field_original.file_resources
        self.global_resources_update = self.field_update.file_resources
        self.local_resource_original = self.field_original.message_resource
        self.local_resource_update = self.field_update.message_resource

        # 3. If both FieldDescriptors are existing, check
        # if the name is changed.
        if self.field_original.name != self.field_update.name:
            self.finding_container.addFinding(
                category=FindingCategory.FIELD_NAME_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.source_code_line,
                message=f"Name of an existing field is changed from `{self.field_original.name}` to `{self.field_update.name}`.",
                actionable=True,
            )
            return

        # 4. If the FieldDescriptors have the same name, check if the
        # repeated state of them stay the same.
        if self.field_original.repeated.value != self.field_update.repeated.value:
            self.finding_container.addFinding(
                category=FindingCategory.FIELD_REPEATED_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.repeated.source_code_line,
                message=f"Repeated state of an existing field `{self.field_original.name}` is changed.",
                actionable=True,
            )
        # Field option change from optional to required is breaking.
        if not self.field_original.required.value and self.field_update.required.value:
            self.finding_container.addFinding(
                category=FindingCategory.FIELD_BEHAVIOR_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.required.source_code_line,
                message=f"Field behavior of an existing field `{self.field_original.name}` is changed.",
                actionable=True,
            )
        # 5. Check the type of the field.
        if self.field_original.proto_type.value != self.field_update.proto_type.value:
            self.finding_container.addFinding(
                category=FindingCategory.FIELD_TYPE_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=self.field_update.proto_type.source_code_line,
                message=f"Type of an existing field `{self.field_original.name}` is changed from `{self.field_original.proto_type.value}` to `{self.field_update.proto_type.value}`.",
                actionable=True,
            )
        # If field has the same primitive type, then the type is identical.
        # If field has the same non-primitive type like `TYPE_ENUM`.
        # Check the type_name of the field.
        elif self.field_original.type_name and (
            self.field_original.type_name.value != self.field_update.type_name.value
        ):
            # Version update is allowed here, for example from `.example.v1.Enum` to `.example.v1beta1.Enum`.
            # But from `.example.v1.Enum` to `.example.v2.EnumUpdate` is breaking.
            api_version_original = self.field_original.api_version
            api_version_update = self.field_update.api_version
            transformed_type_name = (
                self.field_original.type_name.value.replace(
                    api_version_original, api_version_update
                )
                if api_version_original
                else None
            )
            if (
                not transformed_type_name
                or transformed_type_name != self.field_update.type_name.value
            ):
                self.finding_container.addFinding(
                    category=FindingCategory.FIELD_TYPE_CHANGE,
                    proto_file_name=self.field_update.proto_file_name,
                    source_code_line=self.field_update.type_name.source_code_line,
                    message=f"Type of an existing field `{self.field_original.name}` is changed from `{self.field_original.type_name.value}` to `{self.field_update.type_name.value}`.",
                    actionable=True,
                )
        # 6. Check the oneof_index of the field.
        if self.field_original.oneof != self.field_update.oneof:
            proto_file_name = self.field_update.proto_file_name
            source_code_line = self.field_update.source_code_line
            if self.field_original.oneof:
                msg = f"An existing field `{self.field_original.name}` is moved out of One-of."
                self.finding_container.addFinding(
                    category=FindingCategory.FIELD_ONEOF_REMOVAL,
                    proto_file_name=proto_file_name,
                    source_code_line=source_code_line,
                    message=msg,
                    actionable=True,
                )
            else:
                msg = f"An existing field `{self.field_original.name}` is moved into One-of."
                self.finding_container.addFinding(
                    category=FindingCategory.FIELD_ONEOF_ADDITION,
                    proto_file_name=proto_file_name,
                    source_code_line=source_code_line,
                    message=msg,
                    actionable=True,
                )

        # 6. Check `google.api.resource_reference` annotation.
        self._compare_resource_reference(self.field_original, self.field_update)

    def _compare_resource_reference(self, field_original, field_update):
        resource_ref_original = self.field_original.resource_reference
        resource_ref_update = self.field_update.resource_reference
        # No resource_reference annotations found for the field in both versions.
        if not resource_ref_original and not resource_ref_update:
            return
        # A `google.api.resource_reference` annotation is added.
        if not resource_ref_original and resource_ref_update:
            self.finding_container.addFinding(
                category=FindingCategory.RESOURCE_REFERENCE_ADDITION,
                proto_file_name=field_update.proto_file_name,
                source_code_line=resource_ref_update.source_code_line,
                message=f"A resource reference option is added to the field `{field_original.name}`.",
                actionable=False,
            )
            return
        # Resource annotation is removed, check if it is added as a message resource.
        if resource_ref_original and not resource_ref_update:
            if not self._resource_ref_in_local(resource_ref_original.value):
                self.finding_container.addFinding(
                    category=FindingCategory.RESOURCE_REFERENCE_REMOVAL,
                    proto_file_name=field_original.proto_file_name,
                    source_code_line=resource_ref_original.source_code_line,
                    message=f"A resource reference option of the field `{field_original.name}` is removed.",
                    actionable=True,
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
                self.finding_container.addFinding(
                    category=FindingCategory.RESOURCE_REFERENCE_CHANGE,
                    proto_file_name=field_update.proto_file_name,
                    source_code_line=resource_ref_update.source_code_line,
                    message=f"The type of resource reference option of the field `{field_original.name}` is changed from `{original_type}`` to `{update_type}`.",
                    actionabel=True,
                )
            return
        # The `type` is changed to `child_type` or `child_type` is changed to `type`, but
        # resulting referenced resource patterns can be resolved to be identical,
        # in that case it is not considered breaking.
        # Register the message-level resource into the global resource database,
        # so that we can query the parent resources for child_type.
        self._register_local_resource()
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

    def _resource_ref_in_local(self, resource_ref):
        """Check if the resource type is in the local resources defined by a message option."""
        if not self.local_resource_update:
            return False
        checked_type = resource_ref.type or resource_ref.child_type
        if not checked_type:
            raise TypeError(
                "In a resource_reference annotation, either `type` or `child_type` field should be defined"
            )
        if self.local_resource_update.value.type != checked_type:
            return False
        return True

    def _register_local_resource(self):
        # Add message-level resource definition to the global resource database for query.
        if self.local_resource_original:
            self.global_resources_original.register_resource(
                self.local_resource_original
            )
        if self.local_resource_update:
            self.global_resources_update.register_resource(self.local_resource_update)

    def _is_parent_type(
        self, child_type, parent_type, original_is_child, source_code_line
    ):
        if original_is_child:
            parent_resources = (
                self.global_resources_original.get_parent_resources_by_child_type(
                    child_type
                )
            )
        else:
            parent_resources = (
                self.global_resources_update.get_parent_resources_by_child_type(
                    child_type
                )
            )
        if parent_type not in [parent.type for parent in parent_resources]:
            # Resulting referenced resource patterns cannot be resolved identical.
            self.finding_container.addFinding(
                category=FindingCategory.RESOURCE_REFERENCE_CHANGE,
                proto_file_name=self.field_update.proto_file_name,
                source_code_line=source_code_line,
                message=f"The child_type `{child_type}` and type `{parent_type}` of "
                f"resource reference option in field `{self.field_original.name}` "
                "cannot be resolved to the identical resource.",
                actionable=True,
            )

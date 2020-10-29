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

from google.api import resource_pb2
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class FieldComparator:
    def __init__(
        self,
        field_original: FieldDescriptorProto,
        field_update: FieldDescriptorProto,
        global_resources_original=None,
        global_resources_update=None,
        local_resource_original=None,
        local_resource_update=None,
    ):
        self.field_original = field_original
        self.field_update = field_update
        self.global_resources_original = global_resources_original
        self.global_resources_update = global_resources_update
        self.local_resource_original = local_resource_original
        self.local_resource_update = local_resource_update

    def compare(self):
        # 1. If original FieldDescriptor is None, then a
        # new FieldDescriptor is added.
        if self.field_original is None:
            msg = f"A new Field {self.field_update.name} is added."
            FindingContainer.addFinding(FindingCategory.FIELD_ADDITION, "", msg, False)
            return

        # 2. If updated FieldDescriptor is None, then
        # the original FieldDescriptor is removed.
        if self.field_update is None:
            msg = f"A Field {self.field_original.name} is removed"
            FindingContainer.addFinding(FindingCategory.FIELD_REMOVAL, "", msg, True)
            return

        # 3. If both FieldDescriptors are existing, check
        # if the name is changed.
        if self.field_original.name != self.field_update.name:
            msg = f"Name of the Field is changed, the original is {self.field_original.name}, but the updated is {self.field_update.name}"
            FindingContainer.addFinding(
                FindingCategory.FIELD_NAME_CHANGE, "", msg, True
            )
            return

        # 4. If the FieldDescriptors have the same name, check if the
        # repeated state of them stay the same.
        if self.field_original.label != self.field_update.label:
            option_original = FieldDescriptorProto().Label.Name(
                self.field_original.label
            )
            option_update = FieldDescriptorProto().Label.Name(self.field_update.label)
            msg = f"Repeated state of the Field is changed, the original is {option_original}, but the updated is {option_update}"
            FindingContainer.addFinding(
                FindingCategory.FIELD_REPEATED_CHANGE, "", msg, True
            )

        # 5. If the FieldDescriptors have the same repeated state,
        # check if the type of them stay the same.
        if self.field_original.type != self.field_update.type:
            type_original = FieldDescriptorProto().Type.Name(self.field_original.type)
            type_update = FieldDescriptorProto().Type.Name(self.field_update.type)
            msg = f"Type of the field is changed, the original is {type_original}, but the updated is {type_update}"
            FindingContainer.addFinding(
                FindingCategory.FIELD_TYPE_CHANGE, "", msg, True
            )
        # 6. Check the oneof_index of the field.
        oneof_original = self.field_original.HasField("oneof_index")
        oneof_update = self.field_update.HasField("oneof_index")
        if oneof_original != oneof_update:
            if oneof_original:
                msg = f"The existing field {self.field_original.name} is moved out of One-of."
                FindingContainer.addFinding(
                    FindingCategory.FIELD_ONEOF_REMOVAL, "", msg, True
                )
            else:
                msg = f"The existing field {self.field_original.name} is moved into One-of."
                FindingContainer.addFinding(
                    FindingCategory.FIELD_ONEOF_ADDITION, "", msg, True
                )

        # 6. Check `google.api.resource_reference` annotation.
        self._compare_resource_reference(self.field_original, self.field_update)

    def _compare_resource_reference(self, field_original, field_update):
        resource_ref_original = self._get_resource_reference(field_original)
        resource_ref_update = self._get_resource_reference(field_update)
        # No resource_reference option found for the fieldin bothe versions.
        if not resource_ref_original and not resource_ref_update:
            return
        # A `google.api.resource_reference` annotation is added.
        if not resource_ref_original and resource_ref_update:
            FindingContainer.addFinding(
                FindingCategory.RESOURCE_REFERENCE_ADDITION,
                "",
                f"A resource reference option is added to the field {field_original.name}",
                False,
            )
            return
        # Resource annotation is removed, check if it is added as a message resource.
        if resource_ref_original and not resource_ref_update:
            if not self._resource_ref_in_local(resource_ref_original):
                FindingContainer.addFinding(
                    FindingCategory.RESOURCE_REFERENCE_REMOVAL,
                    "",
                    f"A resource reference option of field '{field_original.name}' is removed.",
                    True,
                )
            return
        # Resource annotation is both existing in the field for original and update versions.
        # They both use `type` or `child_type`.
        if (resource_ref_original.type and resource_ref_update.type) or (
            resource_ref_original.child_type and resource_ref_update.child_type
        ):
            original_type = (
                resource_ref_original.type or resource_ref_original.child_type
            )
            update_type = resource_ref_update.type or resource_ref_update.child_type
            if original_type != update_type:
                FindingContainer.addFinding(
                    FindingCategory.RESOURCE_REFERENCE_CHANGE,
                    "",
                    f"The type of resource reference option in field '{field_original.name}' is changed from '{original_type}' to '{update_type}'.",
                    True,
                )
            return
        # The `type` is changed to `child_type` or `child_type` is changed to `type`, but
        # resulting referenced resource patterns resolve to be identical, in that case it
        # is not considered breaking.
        self._register_local_resource()
        if resource_ref_original.child_type and resource_ref_update.type:
            parent_resources = (
                self.global_resources_original.get_parent_resources_by_child_type(
                    resource_ref_original.child_type
                )
            )
            if resource_ref_update.type not in [
                parent.type for parent in parent_resources
            ]:
                # Resulting referenced resource patterns cannot be resolved identical.
                FindingContainer.addFinding(
                    FindingCategory.RESOURCE_REFERENCE_CHANGE,
                    "",
                    f"The original child_type '{resource_ref_original.child_type}' and updated type '{resource_ref_update.type}' of resource reference option in field '{field_original.name}' cannot be resolved to the identical resource.",
                    True,
                )
        if resource_ref_original.type and resource_ref_update.child_type:
            parent_resources = (
                self.global_resources_update.get_parent_resources_by_child_type(
                    resource_ref_update.child_type
                )
            )
            if resource_ref_original.type not in [
                parent.type for parent in parent_resources
            ]:
                # Resulting referenced resource patterns cannot be resolved identical.
                FindingContainer.addFinding(
                    FindingCategory.RESOURCE_REFERENCE_CHANGE,
                    "",
                    f"The original type '{resource_ref_original.type}' and updated child_type '{resource_ref_update.child_type}' of resource reference option in field '{field_original.name}' cannot be resolved to the identical resource.",
                    True,
                )

    def _get_resource_reference(self, field):
        reference = field.options.Extensions[resource_pb2.resource_reference]
        if not reference.type and not reference.child_type:
            return None
        return reference

    def _resource_ref_in_local(self, resource_ref):
        """Check if the resource type is in the local resources defined by a message option."""
        if not self.local_resource_update:
            return False
        checked_type = resource_ref.type or resource_ref.child_type
        if not checked_type:
            raise TypeError(
                "In a resource_reference annotation, either `type` or `child_type` field should be defined"
            )
        if self.local_resource_update.type != checked_type:
            return False
        return True

    def _register_local_resource(self):
        # Add message-level resource definition to the global resource database for query.
        self.global_resources_original.register_resource(self.local_resource_original)
        self.global_resources_update.register_resource(self.local_resource_update)

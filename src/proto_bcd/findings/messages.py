# Copyright 2021 Google LLC
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


from collections import defaultdict
from types import MappingProxyType
from proto_bcd.findings.finding_category import FindingCategory

_templates = defaultdict(lambda: "Unknown change type")
_templates[
    FindingCategory.ENUM_VALUE_ADDITION
] = "A new value `{subject}` is added to enum `{context}`."
_templates[
    FindingCategory.ENUM_VALUE_REMOVAL
] = "An existing value `{subject}` is removed from enum `{context}`."
_templates[
    FindingCategory.ENUM_VALUE_NAME_CHANGE
] = "Existing value `{oldsubject}` is renamed to `{subject}` in enum `{context}`."
_templates[
    FindingCategory.ENUM_VALUE_NUMBER_CHANGE
] = "Existing value `{oldsubject}` is changed to `{subject}` in enum `{context}`."
_templates[FindingCategory.ENUM_ADDITION] = "A new enum `{subject}` is added."
_templates[FindingCategory.ENUM_REMOVAL] = "An existing enum `{subject}` is removed."
_templates[
    FindingCategory.FIELD_ADDITION
] = "A new field `{subject}` is added to message `{context}`."
_templates[
    FindingCategory.FIELD_REMOVAL
] = "An existing field `{subject}` is removed from message `{context}`."
_templates[
    FindingCategory.FIELD_NAME_CHANGE
] = "An existing field `{oldsubject}` is renamed to `{subject}` in message `{context}`."
_templates[
    FindingCategory.FIELD_REPEATED_CHANGE
] = "Changed repeated flag of an existing field `{subject}` in message `{context}`."
_templates[
    FindingCategory.FIELD_TYPE_CHANGE
] = "The type of an existing field `{subject}` is changed from `{oldtype}` to `{type}` in message `{context}`."
_templates[
    FindingCategory.FIELD_ONEOF_MOVE_OUT
] = "An existing field `{subject}` is moved out of oneof in message `{context}`."
_templates[
    FindingCategory.FIELD_ONEOF_MOVE_IN
] = "An existing field `{subject}` is moved in to oneof in message `{context}`."
_templates[
    FindingCategory.FIELD_PROTO3_OPTIONAL_CHANGE
] = "Changed proto3 optional flag of an existing field `{subject}` in message `{context}`."
_templates[
    FindingCategory.FIELD_BEHAVIOR_CHANGE
] = "Changed field behavior for an existing field `{subject}` in message `{context}`."
_templates[
    FindingCategory.FIELD_FORMAT_CHANGE
] = "Changed field format for an existing field `{subject}` in message `{context}`."
_templates[
    FindingCategory.RESOURCE_REFERENCE_REMOVAL
] = "An existing resource_reference option of the field `{subject}` is removed in message `{context}`."
_templates[
    FindingCategory.RESOURCE_REFERENCE_ADDITION
] = "A new resource_reference option is added to the field `{subject}` in message `{context}`."
_templates[
    FindingCategory.RESOURCE_REFERENCE_CHANGE
] = "A type of an existing resource_reference option of the field `{subject}` in message `{context}` is changed from `{oldtype}` to `{type}`."
_templates[
    FindingCategory.RESOURCE_REFERENCE_MOVED
] = "An existing resource_reference option of the field `{subject}` is removed from message `{context}` but moved to another message."
_templates[
    FindingCategory.RESOURCE_REFERENCE_CHANGE_CHILD_TYPE
] = "The child_type `{oldtype}` and type `{type}` of resource_reference option in field `{subject}` of message `{context}` cannot be resolved to the identical resource."
_templates[FindingCategory.MESSAGE_ADDITION] = "A new message `{subject}` is added."
_templates[
    FindingCategory.MESSAGE_REMOVAL
] = "An existing message `{subject}` is removed."
_templates[
    FindingCategory.MESSAGE_MOVED_TO_ANOTHER_FILE
] = "An existing message `{subject}` is moved from `{oldcontext}` to `{context}`."
_templates[
    FindingCategory.RESOURCE_DEFINITION_ADDITION
] = "A new resource_definition `{subject}` is added."
_templates[
    FindingCategory.RESOURCE_DEFINITION_REMOVAL
] = "An existing resource_definition `{subject}` is removed."
_templates[
    FindingCategory.RESOURCE_PATTERN_REMOVAL
] = "An existing resource pattern value `{type}` from the resource definition `{subject}` is removed."
_templates[
    FindingCategory.RESOURCE_PATTERN_REORDER
] = "An existing resource's patterns were reordered in `{subject}`."
_templates[
    FindingCategory.RESOURCE_PATTERN_ADDITION
] = "A new resource pattern value `{type}` added to the resource definition `{subject}`."
_templates[FindingCategory.SERVICE_ADDITION] = "A new service `{subject}` is added."
_templates[
    FindingCategory.SERVICE_REMOVAL
] = "An existing service `{subject}` is removed."
_templates[
    FindingCategory.SERVICE_HOST_ADDITION
] = "A new default host `{subject}` is added to service `{context}`."
_templates[
    FindingCategory.SERVICE_HOST_REMOVAL
] = "An existing default host `{subject}` is removed from service `{context}`."
_templates[
    FindingCategory.SERVICE_HOST_CHANGE
] = "An existing default host `{oldsubject}` is changed to `{subject}` in service `{context}`."
_templates[
    FindingCategory.METHOD_SIGNATURE_REMOVAL
] = "An existing method_signature `{type}` is removed from method `{subject}` in service `{context}`."
_templates[
    FindingCategory.METHOD_SIGNATURE_ADDITION
] = "A new method_signature `{type}` is added to method `{subject}` in service `{context}`."
_templates[
    FindingCategory.METHOD_SIGNATURE_ORDER_CHANGE
] = "An existing method_signature `{type}` has changed its position in method `{subject}` in service `{context}`."
_templates[
    FindingCategory.OAUTH_SCOPE_REMOVAL
] = "An existing oauth_scope `{subject}` is removed from service `{context}`."
_templates[
    FindingCategory.OAUTH_SCOPE_ADDITION
] = "A new oauth_scope `{subject}` is added to service `{context}`."
_templates[
    FindingCategory.METHOD_REMOVAL
] = "An existing method `{subject}` is removed from service `{context}`."
_templates[
    FindingCategory.METHOD_ADDITION
] = "A new method `{subject}` is added to service `{context}`."
_templates[
    FindingCategory.METHOD_INPUT_TYPE_CHANGE
] = "Input type of method `{subject}` is changed from `{oldtype}` to `{type}` in service `{context}`."
_templates[
    FindingCategory.METHOD_RESPONSE_TYPE_CHANGE
] = "Response type of method `{subject}` is changed from `{oldtype}` to `{type}` in service `{context}`."
_templates[
    FindingCategory.METHOD_CLIENT_STREAMING_CHANGE
] = "Client streaming flag is changed for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.METHOD_SERVER_STREAMING_CHANGE
] = "Server streaming flag is changed for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE
] = "Pagination feature is changed for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.LRO_RESPONSE_CHANGE
] = "Long running operation response type is changed from `{oldtype}` to `{type}` for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.LRO_METADATA_CHANGE
] = "Long running operation metadata type is changed from `{oldtype}` to `{type}` for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.LRO_ANNOTATION_ADDITION
] = "New long running annotation is added for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.LRO_ANNOTATION_REMOVAL
] = "Existing long running annitation is removed from method `{subject}` in service `{context}`."
_templates[
    FindingCategory.HTTP_ANNOTATION_CHANGE
] = "An existing google.api.http annotation `{type}` is changed for method `{subject}` in service `{context}`."
_templates[
    FindingCategory.HTTP_ANNOTATION_REMOVAL
] = "An existing google.api.http annotation is removed from method `{subject}` in service `{context}`."
_templates[
    FindingCategory.HTTP_ANNOTATION_ADDITION
] = "A new google.api.http annotation is added to method `{subject}` in service `{context}`."
_templates[
    FindingCategory.PACKAGING_OPTION_REMOVAL
] = "An existing packaging option `{type}` for `{subject}` is removed."
_templates[
    FindingCategory.PACKAGING_OPTION_ADDITION
] = "A new packaging option `{type}` for `{subject}` is added."
_templates[
    FindingCategory.SERVICE_COMMENT_CHANGE
] = "A comment for service `{subject}` is changed."
_templates[
    FindingCategory.METHOD_COMMENT_CHANGE
] = "A comment for method `{subject}` in service `{context}` is changed."
_templates[
    FindingCategory.MESSAGE_COMMENT_CHANGE
] = "A comment for message `{subject}` is changed."
_templates[
    FindingCategory.FIELD_COMMENT_CHANGE
] = "A comment for field `{subject}` in message `{context}` is changed."
_templates[
    FindingCategory.ENUM_COMMENT_CHANGE
] = "A comment for enum `{subject}` is changed."
_templates[
    FindingCategory.ENUM_VALUE_COMMENT_CHANGE
] = "A comment for enum value `{subject}` in enum `{context}` is changed."

templates = MappingProxyType(_templates)

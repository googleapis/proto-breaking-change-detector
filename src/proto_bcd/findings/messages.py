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
_templates[FindingCategory.ENUM_VALUE_ADDITION] = (
    "add enum value `{context}.{subject}`."
)
_templates[FindingCategory.ENUM_VALUE_REMOVAL] = (
    "remove enum value `{context}.{subject}`."
)
_templates[FindingCategory.ENUM_VALUE_NAME_CHANGE] = (
    "rename enum value `{context}.{oldsubject}` to `{context}.{subject}`."
)
_templates[FindingCategory.ENUM_VALUE_NUMBER_CHANGE] = (
    "change enum value `{context}.{oldsubject}` to `{context}.{subject}`."
)
_templates[FindingCategory.ENUM_ADDITION] = "add enum `{subject}`."
_templates[FindingCategory.ENUM_REMOVAL] = "remove enum `{subject}`."
_templates[FindingCategory.FIELD_ADDITION] = "add field `{context}.{subject}`."
_templates[FindingCategory.FIELD_REMOVAL] = "remove field `{context}.{subject}`."
_templates[FindingCategory.FIELD_NAME_CHANGE] = (
    "rename field `{context}.{oldsubject}` to `{context}.{subject}`."
)
_templates[FindingCategory.FIELD_REPEATED_CHANGE] = (
    "change repeated flag of field `{context}.{subject}`."
)
_templates[FindingCategory.FIELD_TYPE_CHANGE] = (
    "change type of field `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.FIELD_ONEOF_MOVE_OUT] = (
    "move field `{context}.{subject}` out of oneof."
)
_templates[FindingCategory.FIELD_ONEOF_MOVE_IN] = (
    "move field `{context}.{subject}` into oneof."
)
_templates[FindingCategory.FIELD_PROTO3_OPTIONAL_CHANGE] = (
    "change proto3 optional flag of field `{context}.{subject}`."
)
_templates[FindingCategory.FIELD_BEHAVIOR_CHANGE] = (
    "change field behavior of field `{context}.{subject}`."
)
_templates[FindingCategory.NEW_REQUIRED_FIELD] = (
    "add REQUIRED field `{context}.{subject}`."
)
_templates[FindingCategory.FIELD_FORMAT_CHANGE] = (
    "change field format of field `{context}.{subject}`."
)
_templates[FindingCategory.RESOURCE_REFERENCE_REMOVAL] = (
    "remove resource_reference option from field `{context}.{subject}`."
)
_templates[FindingCategory.RESOURCE_REFERENCE_ADDITION] = (
    "add resource_reference option to field `{context}.{subject}`."
)
_templates[FindingCategory.RESOURCE_REFERENCE_CHANGE] = (
    "change resource_reference option type of field `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.RESOURCE_REFERENCE_MOVED] = (
    "move resource_reference option of field `{context}.{subject}` to another message."
)
_templates[FindingCategory.RESOURCE_REFERENCE_CHANGE_CHILD_TYPE] = (
    "change resource_reference option child_type of field `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.MESSAGE_ADDITION] = "add message `{subject}`."
_templates[FindingCategory.MESSAGE_REMOVAL] = "remove message `{subject}`."
_templates[FindingCategory.MESSAGE_MOVED_TO_ANOTHER_FILE] = (
    "move message `{subject}` from `{oldcontext}` to `{context}`."
)
_templates[FindingCategory.RESOURCE_DEFINITION_ADDITION] = (
    "add resource_definition `{subject}`."
)
_templates[FindingCategory.RESOURCE_DEFINITION_REMOVAL] = (
    "remove resource_definition `{subject}`."
)
_templates[FindingCategory.RESOURCE_PATTERN_REMOVAL] = (
    "remove resource pattern value `{type}` from resource definition `{subject}`."
)
_templates[FindingCategory.RESOURCE_PATTERN_REORDER] = (
    "reorder resource patterns of `{subject}`."
)
_templates[FindingCategory.RESOURCE_PATTERN_ADDITION] = (
    "add resource pattern value `{type}` to resource definition `{subject}`."
)
_templates[FindingCategory.SERVICE_ADDITION] = "add service `{subject}`."
_templates[FindingCategory.SERVICE_REMOVAL] = "remove service `{subject}`."
_templates[FindingCategory.SERVICE_HOST_ADDITION] = (
    "add default host `{subject}` to service `{context}`."
)
_templates[FindingCategory.SERVICE_HOST_REMOVAL] = (
    "remove default host `{subject}` from service `{context}`."
)
_templates[FindingCategory.SERVICE_HOST_CHANGE] = (
    "change default host of service `{context}` from `{oldsubject}` to `{subject}`."
)
_templates[FindingCategory.METHOD_SIGNATURE_REMOVAL] = (
    "remove method_signature `{type}` from rpc method `{context}.{subject}`."
)
_templates[FindingCategory.METHOD_SIGNATURE_ADDITION] = (
    "add method_signature `{type}` to rpc method `{context}.{subject}`."
)
_templates[FindingCategory.METHOD_SIGNATURE_ORDER_CHANGE] = (
    "change position of method_signature `{type}` of rpc method `{context}.{subject}`."
)
_templates[FindingCategory.OAUTH_SCOPE_REMOVAL] = (
    "remove oauth_scope `{subject}` from service `{context}`."
)
_templates[FindingCategory.OAUTH_SCOPE_ADDITION] = (
    "add oauth_scope `{subject}` to service `{context}`."
)
_templates[FindingCategory.METHOD_REMOVAL] = "remove rpc method `{context}.{subject}`."
_templates[FindingCategory.METHOD_ADDITION] = "add rpc method `{context}.{subject}`."
_templates[FindingCategory.METHOD_INPUT_TYPE_CHANGE] = (
    "change input type of rpc method `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.METHOD_RESPONSE_TYPE_CHANGE] = (
    "change response type of rpc method `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.METHOD_CLIENT_STREAMING_CHANGE] = (
    "change client streaming flag of rpc method `{context}.{subject}`."
)
_templates[FindingCategory.METHOD_SERVER_STREAMING_CHANGE] = (
    "change server streaming flag of rpc method `{context}.{subject}`."
)
_templates[FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE] = (
    "change pagination feature of rpc method `{context}.{subject}`."
)
_templates[FindingCategory.LRO_RESPONSE_CHANGE] = (
    "change long running operation response type of rpc method `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.LRO_METADATA_CHANGE] = (
    "change long running operation metadata type of rpc method `{context}.{subject}` from `{oldtype}` to `{type}`."
)
_templates[FindingCategory.LRO_ANNOTATION_ADDITION] = (
    "add long running annotation to rpc method `{context}.{subject}`."
)
_templates[FindingCategory.LRO_ANNOTATION_REMOVAL] = (
    "remove long running annitation from rpc method `{context}.{subject}`."
)
_templates[FindingCategory.HTTP_ANNOTATION_CHANGE] = (
    "change google.api.http annotation `{type}` of rpc method `{context}.{subject}`."
)
_templates[FindingCategory.HTTP_ANNOTATION_REMOVAL] = (
    "remove google.api.http annotation from rpc method `{context}.{subject}`."
)
_templates[FindingCategory.HTTP_ANNOTATION_ADDITION] = (
    "add google.api.http annotation to method `{context}.{subject}`."
)
_templates[FindingCategory.PACKAGING_OPTION_REMOVAL] = (
    "remove packaging option `{type}` from `{subject}`."
)
_templates[FindingCategory.PACKAGING_OPTION_ADDITION] = (
    "add packaging option `{type}` to `{subject}`."
)
_templates[FindingCategory.SERVICE_COMMENT_CHANGE] = (
    "change comment of service `{subject}`."
)
_templates[FindingCategory.METHOD_COMMENT_CHANGE] = (
    "change comment of rpc method `{context}.{subject}`."
)
_templates[FindingCategory.MESSAGE_COMMENT_CHANGE] = (
    "change comment of message `{subject}`."
)
_templates[FindingCategory.FIELD_COMMENT_CHANGE] = (
    "change comment of field `{context}.{subject}`."
)
_templates[FindingCategory.ENUM_COMMENT_CHANGE] = "change comment of enum `{subject}`."
_templates[FindingCategory.ENUM_VALUE_COMMENT_CHANGE] = (
    "change comment of enum value `{context}.{subject}`."
)

templates = MappingProxyType(_templates)

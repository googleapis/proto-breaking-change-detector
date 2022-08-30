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

import enum


class FindingCategory(enum.Enum):
    # Enums
    ENUM_VALUE_ADDITION = 1
    ENUM_VALUE_REMOVAL = 2
    ENUM_VALUE_NAME_CHANGE = 3
    ENUM_ADDITION = 4
    ENUM_REMOVAL = 5
    # Fields
    FIELD_ADDITION = 6
    FIELD_REMOVAL = 7
    FIELD_NAME_CHANGE = 8
    FIELD_REPEATED_CHANGE = 9
    FIELD_TYPE_CHANGE = 10
    FIELD_ONEOF_MOVE_OUT = 11
    FIELD_ONEOF_MOVE_IN = 12
    FIELD_PROTO3_OPTIONAL_CHANGE = 13
    # Field annotations
    FIELD_BEHAVIOR_CHANGE = 14
    RESOURCE_REFERENCE_REMOVAL = 15
    RESOURCE_REFERENCE_ADDITION = 16
    RESOURCE_REFERENCE_CHANGE = 17
    RESOURCE_REFERENCE_MOVED = 18
    RESOURCE_REFERENCE_CHANGE_CHILD_TYPE = 19
    # Messages
    MESSAGE_ADDITION = 20
    MESSAGE_REMOVAL = 21
    # Message annotations
    RESOURCE_DEFINITION_ADDITION = 22
    RESOURCE_DEFINITION_REMOVAL = 24
    RESOURCE_PATTERN_REMOVAL = 25
    RESOURCE_PATTERN_ADDITION = 26
    # Services
    SERVICE_ADDITION = 30
    SERVICE_REMOVAL = 31
    # Service annotations
    SERVICE_HOST_ADDITION = 32
    SERVICE_HOST_REMOVAL = 33
    SERVICE_HOST_CHANGE = 34
    METHOD_SIGNATURE_REMOVAL = 35
    METHOD_SIGNATURE_ADDITION = 36
    OAUTH_SCOPE_REMOVAL = 37
    OAUTH_SCOPE_ADDITION = 38
    # Methods
    METHOD_REMOVAL = 40
    METHOD_ADDTION = 41
    METHOD_INPUT_TYPE_CHANGE = 42
    METHOD_RESPONSE_TYPE_CHANGE = 43
    METHOD_CLIENT_STREAMING_CHANGE = 44
    METHOD_SERVER_STREAMING_CHANGE = 45
    METHOD_PAGINATED_RESPONSE_CHANGE = 46
    # Method annotations
    LRO_RESPONSE_CHANGE = 50
    LRO_METADATA_CHANGE = 51
    LRO_ANNOTATION_ADDITION = 52
    LRO_ANNOTATION_REMOVAL = 53
    HTTP_ANNOTATION_CHANGE = 54
    HTTP_ANNOTATION_REMOVAL = 55
    HTTP_ANNOTATION_ADDITION = 56
    # Packaging options
    PACKAGING_OPTION_REMOVAL = 60
    PACKAGING_OPTION_ADDITION = 61


class ChangeType(enum.Enum):
    MAJOR = 1
    MINOR = 2

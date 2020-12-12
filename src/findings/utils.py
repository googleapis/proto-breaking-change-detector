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
    FIELD_ONEOF_REMOVAL = 11
    FIELD_ONEOF_ADDITION = 12
    FIELD_PROTO3_OPTIONAL_CHANGE = 13
    # Field annotations
    FIELD_BEHAVIOR_CHANGE = 14
    RESOURCE_REFERENCE_REMOVAL = 15
    RESOURCE_REFERENCE_ADDITION = 16
    RESOURCE_REFERENCE_CHANGE = 17
    # Messages
    MESSAGE_ADDITION = 18
    MESSAGE_REMOVAL = 19
    # Message annotations
    RESOURCE_DEFINITION_ADDITION = 20
    RESOURCE_DEFINITION_CHANGE = 21
    RESOURCE_DEFINITION_REMOVAL = 22
    # Services
    SERVICE_ADDITION = 23
    SERVICE_REMOVAL = 24
    # Service annotations
    SERVICE_HOST_ADDITION = 25
    SERVICE_HOST_REMOVAL = 26
    SERVICE_HOST_CHANGE = 27
    METHOD_SIGNATURE_CHANGE = 28
    OAUTH_SCOPE_REMOVAL = 29
    # Methods
    METHOD_REMOVAL = 30
    METHOD_ADDTION = 31
    METHOD_INPUT_TYPE_CHANGE = 32
    METHOD_RESPONSE_TYPE_CHANGE = 33
    METHOD_CLIENT_STREAMING_CHANGE = 34
    METHOD_SERVER_STREAMING_CHANGE = 35
    METHOD_PAGINATED_RESPONSE_CHANGE = 36
    # Method annotations
    LRO_RESPONSE_CHANGE = 37
    LRO_METADATA_CHANGE = 38
    LRO_ANNOTATION_ADDITION = 39
    LRO_ANNOTATION_REMOVAL = 40
    HTTP_ANNOTATION_CHANGE = 41
    HTTP_ANNOTATION_REMOVAL = 42
    HTTP_ANNOTATION_ADDITION = 43
    # Packaging options
    PACKAGING_OPTION_REMOVAL = 44
    PACKAGING_OPTION_ADDITION = 45


class ChangeType(enum.Enum):
    MAJOR = 1
    MINOR = 2


class Finding:
    class _Location:
        proto_file_name: str
        source_code_line: int

        def __init__(self, proto_file_name, source_code_line):
            self.proto_file_name = proto_file_name
            self.source_code_line = source_code_line

    def __init__(
        self,
        category,
        proto_file_name,
        source_code_line,
        message,
        change_type,
        extra_info=None,
    ):
        self.category = category
        self.location = self._Location(proto_file_name, source_code_line)
        self.message = message
        self.change_type = change_type
        self.extra_info = extra_info

    def toDict(self):
        return {
            "category": self.category.name,
            "location": {
                "proto_file_name": self.location.proto_file_name,
                "source_code_line": self.location.source_code_line,
            },
            "message": self.message,
            "change_type": self.change_type.name,
            "extra_info": self.extra_info,
        }

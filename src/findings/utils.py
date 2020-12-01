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
    ENUM_VALUE_ADDITION = 1
    ENUM_VALUE_REMOVAL = 2
    ENUM_VALUE_NAME_CHANGE = 3
    ENUM_ADDITION = 4
    ENUM_REMOVAL = 5
    ENUM_NAME_CHANGE = 6
    FIELD_ADDITION = 7
    FIELD_REMOVAL = 8
    FIELD_NAME_CHANGE = 9
    FIELD_REPEATED_CHANGE = 10
    FIELD_TYPE_CHANGE = 11
    FIELD_ONEOF_REMOVAL = 12
    FIELD_ONEOF_ADDITION = 13
    MESSAGE_ADDITION = 14
    MESSAGE_REMOVAL = 15
    MESSAGE_NAME_CHANEG = 16
    SERVICE_ADDITION = 17
    SERVICE_REMOVAL = 18
    METHOD_REMOVAL = 19
    METHOD_ADDTION = 20
    METHOD_INPUT_TYPE_CHANGE = 21
    METHOD_RESPONSE_TYPE_CHANGE = 22
    METHOD_CLIENT_STREAMING_CHANGE = 23
    METHOD_SERVER_STREAMING_CHANGE = 24
    METHOD_PAGINATED_RESPONSE_CHANGE = 25
    # Annotations
    METHOD_SIGNATURE_CHANGE = 26
    LRO_RESPONSE_CHANGE = 27
    LRO_METADATA_CHANGE = 28
    LRO_ANNOTATION_ADDITION = 29
    LRO_ANNOTATION_REMOVAL = 30
    HTTP_ANNOTATION_CHANGE = 31
    HTTP_ANNOTATION_REMOVAL = 32
    HTTP_ANNOTATION_ADDITION = 33
    RESOURCE_DEFINITION_ADDITION = 34
    RESOURCE_DEFINITION_CHANGE = 35
    RESOURCE_DEFINITION_REMOVAL = 36
    RESOURCE_REFERENCE_REMOVAL = 37
    RESOURCE_REFERENCE_ADDITION = 38
    RESOURCE_REFERENCE_CHANGE = 39
    # Packaging options
    PACKAGING_OPTION_REMOVAL = 40
    PACKAGING_OPTION_ADDITION = 41
    PACKAGING_OPTION_CHANGE = 42
    # Service options
    OAUTH_SCOPE_REMOVAL = 43
    # Field Options
    FIELD_BEHAVIOR_CHANGE = 44


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

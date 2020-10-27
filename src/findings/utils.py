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
    RESOURCE_DEFINITION_ADDITION = 34
    RESOURCE_DEFINITION_CHANGE = 35


class Finding:
    class _Location:
        path: str

        def __init__(self, path):
            self.path = path

    def __init__(self, category, path, message, actionable, extra_info=None):
        self.category = category
        self.location = self._Location(path)
        self.message = message
        self.actionable = actionable
        self.extra_info = extra_info
        self._path = path

    def toDict(self):
        return {
            "category": self.category.value,
            "location": {
                "path": self._path,
            },
            "message": self.message,
            "actionable": self.actionable,
            "extra_info": self.extra_info,
        }

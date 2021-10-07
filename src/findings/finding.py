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


from src.findings.messages import templates


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
        change_type,
        extra_info=None,
        subject="",
        oldsubject="",
        context="",
        type="",
        oldtype="",
    ):
        self.category = category
        self.location = self._Location(proto_file_name, source_code_line)
        self.change_type = change_type
        self.extra_info = extra_info
        self.subject = subject
        self.oldsubject = oldsubject
        self.context = context
        self.type = type
        self.oldtype = oldtype

    def toDict(self):
        return {
            "category": self.category.name,
            "location": {
                "proto_file_name": self.location.proto_file_name,
                "source_code_line": self.location.source_code_line,
            },
            "change_type": self.change_type.name,
            "extra_info": self.extra_info,
            "subject": self.subject,
            "oldsubject": self.oldsubject,
            "context": self.context,
            "type": self.type,
            "oldtype": self.oldtype,
        }

    def getMessage(self):
        format_parameters = self.toDict()
        return templates[self.category].format(**format_parameters)

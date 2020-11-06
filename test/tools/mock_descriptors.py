# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Tuple
from google.protobuf import descriptor_pb2 as desc
import src.comparator.wrappers as wrappers


def make_enum_value_pb2(
    name: str, number: int, **kwargs
) -> desc.EnumValueDescriptorProto:
    return desc.EnumValueDescriptorProto(name=name, number=number)


def make_enum_value(
    name: str,
    number: int,
    proto_file_name: str = "foo",
    source_code_locations: Dict[Tuple[int, ...], desc.SourceCodeInfo.Location] = {},
    path: Tuple[int] = (),
) -> wrappers.EnumValue:
    enum_value_pb = make_enum_value_pb2(name, number)
    enum_value = wrappers.EnumValue(
        enum_value_pb, proto_file_name, source_code_locations, path
    )
    return enum_value

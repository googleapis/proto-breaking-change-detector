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

from typing import Dict, Tuple, Sequence
from google.protobuf import descriptor_pb2 as desc
import src.comparator.wrappers as wrappers


def make_enum_value_pb2(
    name: str, number: int, **kwargs
) -> desc.EnumValueDescriptorProto:
    """Mock an EnumValueDescriptorProto that is used to create wrappers.EnumValue"""
    return desc.EnumValueDescriptorProto(name=name, number=number)


def make_enum_value(
    name: str,
    number: int,
    proto_file_name: str = "foo",
    locations: Sequence[desc.SourceCodeInfo.Location] = [],
    path: Tuple[int] = (),
) -> wrappers.EnumValue:
    """Mock an EnumValue object."""
    source_code_locations = {tuple(location.path): location for location in locations}
    enum_value_pb = make_enum_value_pb2(name, number)
    enum_value = wrappers.EnumValue(
        enum_value_pb, proto_file_name, source_code_locations, path
    )
    return enum_value


def make_enum_pb2(
    name: str, values: Tuple[str, int], **kwargs
) -> desc.EnumDescriptorProto:
    """Mock an EnumDescriptorProto that is used to create wrappers.Enum"""
    enum_value_pbs = [make_enum_value_pb2(name=i[0], number=i[1]) for i in values]
    enum_pb = desc.EnumDescriptorProto(name=name, value=enum_value_pbs, **kwargs)
    return enum_pb


def make_enum(
    name: str,
    values: Tuple[str, int] = (),
    proto_file_name: str = "foo",
    locations: Sequence[desc.SourceCodeInfo.Location] = [],
    path: Tuple[int] = (),
) -> wrappers.Enum:
    """Mock an Enum object."""
    source_code_locations = {tuple(location.path): location for location in locations}
    enum_pb = make_enum_pb2(name, values)
    return wrappers.Enum(enum_pb, proto_file_name, source_code_locations, path)

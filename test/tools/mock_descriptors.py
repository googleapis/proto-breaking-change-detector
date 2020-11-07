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

from typing import Tuple, Sequence
from google.protobuf import descriptor_pb2 as desc
import src.comparator.wrappers as wrappers
from src.comparator.resource_database import ResourceDatabase
from google.api import resource_pb2


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


def make_field_pb2(
    name: str,
    number: int,
    label: int,
    proto_type: int,
    type_name: str = None,
    oneof_index: int = None,
    options: desc.FieldOptions = None,
    **kwargs,
) -> desc.FieldDescriptorProto:

    return desc.FieldDescriptorProto(
        name=name,
        number=number,
        label=label,
        type=proto_type,
        type_name=type_name,
        oneof_index=oneof_index,
        options=options,
        **kwargs,
    )


def make_field(
    name: str = "my_field",
    number: int = 1,
    proto_type: str = "TYPE_MESSAGE",
    type_name: str = None,
    repeated: bool = False,
    oneof: bool = False,
    options: desc.FieldOptions = None,
    file_resources: ResourceDatabase = None,
    message_resource: resource_pb2.ResourceDescriptor = None,
    proto_file_name: str = "foo",
    locations: Sequence[desc.SourceCodeInfo.Location] = [],
    path: Tuple[int] = (),
    **kwargs,
) -> wrappers.Field:
    T = desc.FieldDescriptorProto.Type
    type_value = T.Value(proto_type)
    label = 3 if repeated else 1
    oneof_index = 0 if oneof else None

    field_pb = make_field_pb2(
        name=name,
        number=number,
        label=label,
        proto_type=type_value,
        type_name=type_name,
        oneof_index=oneof_index,
        options=options,
        **kwargs,
    )

    source_code_locations = {tuple(location.path): location for location in locations}

    return wrappers.Field(
        field_pb=field_pb,
        proto_file_name=proto_file_name,
        source_code_locations=source_code_locations,
        path=path,
        file_resources=file_resources,
        message_resource=message_resource,
    )

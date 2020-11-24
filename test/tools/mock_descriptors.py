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

from typing import Tuple, Sequence, Dict
from google.protobuf import descriptor_pb2 as desc
import src.comparator.wrappers as wrappers
from src.comparator.resource_database import ResourceDatabase
from google.api import resource_pb2, client_pb2, annotations_pb2
from google.longrunning import operations_pb2  # type: ignore


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


def make_message_pb2(
    name: str,
    fields: tuple = (),
    nested_type: tuple = (),
    enum_type: tuple = (),
    options: desc.MessageOptions = None,
    **kwargs,
) -> desc.DescriptorProto:
    return desc.DescriptorProto(
        name=name,
        field=fields,
        nested_type=nested_type,
        enum_type=enum_type,
        options=options,
        **kwargs,
    )


def make_message(
    name: str = "my_message",
    fields: Sequence[wrappers.Field] = (),
    nested_enums: Sequence[wrappers.Enum] = (),
    nested_messages: Sequence[wrappers.Message] = (),
    proto_file_name: str = "foo",
    locations: Sequence[desc.SourceCodeInfo.Location] = [],
    path: Tuple[int] = (),
    file_resources: ResourceDatabase = None,
    options: desc.MessageOptions = None,
    **kwargs,
) -> wrappers.Message:
    message_pb = make_message_pb2(
        name=name,
        fields=[i.field_pb for i in fields],
        enum_type=[i.enum_pb for i in nested_enums],
        nested_type=[i.message_pb for i in nested_messages],
        options=options,
        **kwargs,
    )

    source_code_locations = {tuple(location.path): location for location in locations}

    return wrappers.Message(
        message_pb=message_pb,
        proto_file_name=proto_file_name,
        source_code_locations=source_code_locations,
        path=path,
        file_resources=file_resources,
        **kwargs,
    )


def make_method_pb2(
    name: str,
    input_type: str,
    output_type: str,
    client_streaming: bool = False,
    server_streaming: bool = False,
    **kwargs,
) -> desc.MethodDescriptorProto:
    # Create the method pb2.
    return desc.MethodDescriptorProto(
        name=name,
        input_type=input_type,
        output_type=output_type,
        client_streaming=client_streaming,
        server_streaming=server_streaming,
        **kwargs,
    )


def make_method(
    name: str,
    input_message: wrappers.Message = None,
    output_message: wrappers.Message = None,
    client_streaming: bool = False,
    server_streaming: bool = False,
    signatures: Sequence[str] = (),
    lro_response_type: str = None,
    lro_metadata_type: str = None,
    http_method: str = "get",
    http_uri: str = None,
    http_body: str = None,
    messages_map: Dict[str, wrappers.Message] = {},
    proto_file_name: str = "foo",
    locations: Sequence[desc.SourceCodeInfo.Location] = [],
    path: Tuple[int] = (),
    **kwargs,
) -> wrappers.Method:
    # Use default input and output messages if they are not provided.
    input_message = input_message or make_message("MethodInput")
    output_message = output_message or make_message("MethodOutput")

    method_pb = make_method_pb2(
        name=name,
        input_type=input_message.name,
        output_type=output_message.name,
        client_streaming=client_streaming,
        server_streaming=server_streaming,
        **kwargs,
    )

    # If there are signatures, include them.
    for sig in signatures:
        ext_key = client_pb2.method_signature
        method_pb.options.Extensions[ext_key].append(sig)

    # If there are LRO annotations, include them.
    if lro_response_type and lro_metadata_type:
        method_pb.options.Extensions[operations_pb2.operation_info].MergeFrom(
            operations_pb2.OperationInfo(
                response_type=lro_response_type,
                metadata_type=lro_metadata_type,
            )
        )
    # If there are HTTP annotations, include them.
    if http_method and http_uri and http_body:
        http_annotation = method_pb.options.Extensions[annotations_pb2.http]
        http_annotation.get = http_uri
        http_annotation.body = http_body

    source_code_locations = {tuple(location.path): location for location in locations}
    # Instantiate the wrapper class.
    return wrappers.Method(
        method_pb=method_pb,
        messages_map=messages_map,
        proto_file_name=proto_file_name,
        source_code_locations=source_code_locations,
        path=path,
    )


def make_service_pb2(
    name: str, methods: Sequence[desc.MethodDescriptorProto] = ()
) -> desc.ServiceDescriptorProto:
    return desc.ServiceDescriptorProto(name=name, method=methods)


def make_service(
    name: str = "Placeholder",
    host: str = "",
    methods: Tuple[wrappers.Method] = (),
    scopes: Tuple[str] = (),
    messages_map: Dict[str, wrappers.Message] = {},
    proto_file_name: str = "foo",
    locations: Sequence[desc.SourceCodeInfo.Location] = [],
    path: Tuple[int] = (),
    api_version: str = None,
    **kwargs,
) -> wrappers.Service:
    method_pbs = [m.method_pb for m in methods]
    # Define a service descriptor, and set a host and oauth scopes if
    # appropriate.
    service_pb = make_service_pb2(name=name, methods=method_pbs)
    if host:
        service_pb.options.Extensions[client_pb2.default_host] = host
    service_pb.options.Extensions[client_pb2.oauth_scopes] = ",".join(scopes)

    source_code_locations = {tuple(location.path): location for location in locations}
    # Return a service object to test.
    return wrappers.Service(
        service_pb=service_pb,
        messages_map=messages_map,
        proto_file_name=proto_file_name,
        source_code_locations=source_code_locations,
        path=path,
        api_version=api_version,
    )


def make_file_pb2(
    name: str = "my_proto.proto",
    package: str = "example.v1",
    messages: Sequence[wrappers.Message] = (),
    enums: Sequence[wrappers.Enum] = (),
    services: Sequence[wrappers.Service] = (),
    locations: Sequence[desc.SourceCodeInfo.Location] = (),
    options: desc.FileOptions = None,
    dependency: Sequence[str] = [],
    **kwargs,
) -> desc.FileDescriptorProto:
    return desc.FileDescriptorProto(
        name=name,
        package=package,
        message_type=[m.message_pb for m in messages],
        enum_type=[e.enum_pb for e in enums],
        service=[s.service_pb for s in services],
        source_code_info=desc.SourceCodeInfo(location=locations),
        options=options,
        dependency=dependency,
    )


def make_file_set(
    files: Sequence[desc.FileDescriptorProto] = (),
) -> wrappers.FileSet:
    return wrappers.FileSet(
        file_set_pb=desc.FileDescriptorSet(file=files),
    )

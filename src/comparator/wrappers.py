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

"""Module containing wrapper classes around meta-descriptors.

This module contains dataclasses which wrap the descriptor protos
defined in google/protobuf/descriptor.proto (which are descriptors that
describe descriptors).

"""

import dataclasses
import re
from collections import defaultdict
from google.api import field_behavior_pb2
from google.api import resource_pb2
from google.api import client_pb2
from google.api import annotations_pb2
from google.longrunning import operations_pb2
from google.protobuf import descriptor_pb2
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from src.comparator.resource_database import ResourceDatabase
from typing import Dict, Sequence, Optional, Tuple


def _get_source_code_line(source_code_locations, path):
    if path not in source_code_locations:
        return f"No source code line can be identified by path {path}."
    # The line number in `span` is zero-based, +1 to get the actual line number in .proto file.
    return source_code_locations[path].span[0] + 1


class WithLocation:
    """Wrap the attribute with location information."""

    def __init__(self, value, source_code_locations, path, proto_file_name=None):
        self.value = value
        self.path = path
        self.source_code_locations = source_code_locations
        self.proto_file_name = proto_file_name

    @property
    def source_code_line(self):
        return _get_source_code_line(self.source_code_locations, self.path)


@dataclasses.dataclass(frozen=True)
class EnumValue:
    """Description of an enum value.

    enum_value_pb: the descriptor of EnumValue.
    proto_file_name: the proto file where the EnumValue exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the EnumValue, by querying the above dictionary using the path,
          we can get the location information.
    """

    enum_value_pb: descriptor_pb2.EnumValueDescriptorProto
    proto_file_name: str
    source_code_locations: Dict[Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location]
    path: Tuple[int]

    def __getattr__(self, name):
        return getattr(self.enum_value_pb, name)

    @property
    def source_code_line(self):
        """Return the start line number of EnumValue definition in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


@dataclasses.dataclass(frozen=True)
class Enum:
    """Description of an enum.

    enum_pb: the descriptor of Enum.
    proto_file_name: the proto file where the Enum exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the Enum, by querying the above dictionary using the path,
          we can get the location information.
    """

    enum_pb: descriptor_pb2.EnumDescriptorProto
    proto_file_name: str
    source_code_locations: Dict[Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location]
    path: Tuple[int]

    def __getattr__(self, name):
        return getattr(self.enum_pb, name)

    @property
    def values(self) -> Dict[int, EnumValue]:
        """Return EnumValues in this Enum.

        Returns:
            Dict[int, EnumValue]: EnumValue is identified by number.
        """
        return {
            enum_value.number: EnumValue(
                enum_value,
                self.proto_file_name,
                self.source_code_locations,
                # EnumDescriptorProto.value has field number 2.
                # So we append (2, value_index) to the path.
                self.path + (2, i),
            )
            for i, enum_value in enumerate(self.enum_pb.value)
        }

    @property
    def source_code_line(self):
        """Return the start line number of Enum definition in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Field:
    """Description of a field.

    field_pb: the descriptor of Field.
    proto_file_name: the proto file where the Field exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the Field, by querying the above dictionary using the path,
          we can get the location information.
    resource_database: global resource database that contains all file-level resource definitions
                           and message-level resource options.
    message_resource: message-level resource definition.
    api_version: the version of the API definition files.
    map_entry: type of the field if it is a map.
    """

    def __init__(
        self,
        field_pb: FieldDescriptorProto,
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
        resource_database: ResourceDatabase = None,
        message_resource: resource_pb2.ResourceDescriptor = None,
        api_version: str = None,
        map_entry=None,
    ):

        self.field_pb = field_pb
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path
        # We need the resource database information to determine if the removal or change
        # of the resource_reference annotation is breaking or not.
        self.resource_database = resource_database
        self.message_resource = message_resource
        self.api_version = api_version
        self.map_entry = map_entry

    def __getattr__(self, name):
        return getattr(self.field_pb, name)

    @property
    def name(self):
        """Return the name of the field."""
        return self.field_pb.name

    @property
    def number(self):
        """Return the number of the field."""
        return self.field_pb.number

    @property
    def repeated(self) -> bool:
        """Return True if this is a repeated field, False otherwise.

        Returns:
            bool: Whether this field is repeated.
        """
        # For proto3, only LABEL_REPEATED is explicitly specified which has a path.
        label_repeated = (
            FieldDescriptorProto().Label.Name(self.field_pb.label) == "LABEL_REPEATED"
        )
        # FieldDescriptorProto.label has field number 4.
        return WithLocation(
            label_repeated,
            self.source_code_locations,
            self.path + (4,) if label_repeated else self.path,
        )

    @property
    def required(self):
        """Return True if this field is required, False otherwise.

        Returns:
            bool: Whether this field is required in field_behavior annotation.
        """
        required = (
            field_behavior_pb2.FieldBehavior.Value("REQUIRED")
            in self.field_pb.options.Extensions[field_behavior_pb2.field_behavior]
        )
        # fmt: off
        return WithLocation(
            required,
            self.source_code_locations,
            # FieldOption has field number 8, field_behavior has field
            # number 1052. One field can have multiple behaviors and
            # required attribute has index 0.
            self.path + (8, 1052, 0),
        )
        # fmt: on

    @property
    def proto_type(self):
        """Return the proto type constant e.g. `TYPE_ENUM`"""
        # TODO(xiaozhenliu): convert proto type `TYPE_STRING` to `string`.
        return WithLocation(
            FieldDescriptorProto().Type.Name(self.field_pb.type),
            self.source_code_locations,
            # FieldDescriptorProto.type has field number 5.
            self.path + (5,),
        )

    @property
    def is_primitive_type(self):
        """Return true if the proto_type is primitive python type like `TYPE_STRING`"""
        NON_PRIMITIVE_TYPE = ["TYPE_ENUM", "TYPE_MESSAGE", "TYPE_GROUP"]
        return False if self.proto_type.value in NON_PRIMITIVE_TYPE else True

    @property
    def is_map_type(self):
        """Return true if the field is map type."""
        return self.map_entry

    @property
    def type_name(self):
        """Return the type_name if the proto_type is not primitive, return `None` otherwise.
        For message and enum types, this is the name of full type like `.tutorial.example.Enum`"""
        return (
            None
            if self.is_primitive_type
            else WithLocation(
                # FieldDescriptorProto.type_name has field number 6.
                self.field_pb.type_name,
                self.source_code_locations,
                self.path + (6,),
            )
        )

    @property
    def map_entry_type(self):
        if self.is_map_type:
            key_type = (
                self.map_entry["key"].proto_type.value
                if self.map_entry["key"].is_primitive_type
                else self.map_entry["key"].type_name.value
            )
            value_type = (
                self.map_entry["value"].proto_type.value
                if self.map_entry["value"].is_primitive_type
                else self.map_entry["value"].type_name.value
            )
            return {"key": key_type, "value": value_type}
        return None

    @property
    def oneof(self) -> bool:
        """Return if the field is in oneof"""
        return self.field_pb.HasField("oneof_index")

    @property
    def resource_reference(self) -> Optional[resource_pb2.ResourceReference]:
        """Return the resource_reference annotation of the field if any"""
        resource_ref = self.field_pb.options.Extensions[resource_pb2.resource_reference]
        if not resource_ref.type and not resource_ref.child_type:
            return None
        # FieldDescriptorProto.options has field number 8. And `resource_reference` takes field number 1055.
        # If the reference uses `type`, the field number is 1,
        # if the reference uses `child_type`, the field number is 2.
        resource_ref_path = (
            self.path + (8, 1055, 1) if resource_ref.type else self.path + (8, 1055, 2)
        )
        # In some proto definitions, the reference `type` and `child_type` share
        # the same field number 1055.
        if resource_ref_path not in self.source_code_locations:
            resource_ref_path = self.path + (8, 1055)
        return WithLocation(resource_ref, self.source_code_locations, resource_ref_path)

    @property
    def child_type(self) -> bool:
        """Return True if the resource_reference has child_type, False otherwise"""
        resource_ref = self.field_pb.options.Extensions[resource_pb2.resource_reference]
        return True if len(resource_ref.child_type) > 0 else False

    @property
    def source_code_line(self):
        """Return the start line number of Field definition in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Message:
    """Description of a message (defined with the ``message`` keyword).

    message_pb: the descriptor of Message.
    proto_file_name: the proto file where the Message exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the Message, by querying the above dictionary using the path,
          we can get the location information.
    resource_database: global resource database that contains all file-level resource definitions
                           and message-level resource options.
    api_version: the version of the API definition files.
    """

    def __init__(
        self,
        message_pb: descriptor_pb2.DescriptorProto,
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
        resource_database: ResourceDatabase = None,
        api_version: str = None,
    ):
        self.message_pb = message_pb
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path
        self.resource_database = resource_database
        self.api_version = api_version

    def __getattr__(self, name):
        return getattr(self.message_pb, name)

    @property
    def name(self) -> str:
        """Return the name of this message."""
        return self.message_pb.name

    @property
    def fields(self) -> Dict[int, Field]:
        """Return fields in this message.

        Returns:
            Dict[int, Field]: Field is identified by number.
        """
        fields_map = {}
        for i, field in enumerate(self.message_pb.field):
            # Convert field name to pascal case.
            # The auto-generated nested message uses the transformed
            # name of the field (name `first_field` is converted to `FirstFieldEntry`)
            field_map_entry_name = (
                field.name.replace("_", " ").title().replace(" ", "") + "Entry"
            )
            map_entry = (
                self.map_entries[field_map_entry_name]
                if field_map_entry_name in self.map_entries
                else None
            )
            fields_map[field.number] = Field(
                field_pb=field,
                proto_file_name=self.proto_file_name,
                source_code_locations=self.source_code_locations,
                path=self.path + (2, i),
                resource_database=self.resource_database,
                message_resource=self.resource,
                api_version=self.api_version,
                map_entry=map_entry,
            )
        return fields_map

    @property
    def nested_messages(self) -> Dict[str, "Message"]:
        """Return the nested messsages in the message. Message is identified by name."""
        # fmt: off
        return {
            message.name: Message(
                message,
                self.proto_file_name,
                self.source_code_locations,
                # DescriptorProto.nested_type has field number 3.
                # So we append (3, nested_message_index) to the path.
                self.path + (3, i,),
                self.resource_database,
            )
            # Exclude the auto-generated map_entries message, since
            # the generated message does not have real source code location.
            # Including those messages in the comparator will fail the source code
            # information extraction.
            for i, message in enumerate(self.message_pb.nested_type)
            if not message.options.map_entry
        }
        # fmt: on

    @property
    def map_entries(self) -> Dict[str, Dict[str, Field]]:
        # If the nested message is auto-generated map entry for the maps field,
        # the message name is fieldName + 'Entry', and it has two nested fields (key, value).
        #
        # For maps fields:
        # map<KeyType, ValueType> map_field = 1;
        # The parsed descriptor looks like:
        #    message MapFieldEntry {
        #        option map_entry = true;
        #        optional KeyType key = 1;
        #        optional ValueType value = 2;
        #    }
        #    repeated MapFieldEntry map_field = 1;
        map_entries = {}
        for message in self.message_pb.nested_type:
            if message.options.map_entry:
                fields = {field.name: field for field in message.field}
                if not fields["key"] or not fields["value"]:
                    raise TypeError(
                        "The auto-generated map entry message should have key and value fields."
                    )
                map_entries[message.name] = {
                    "key": Field(
                        field_pb=fields["key"],
                        source_code_locations=self.source_code_locations,
                        proto_file_name=self.proto_file_name,
                        path=self.path,
                    ),
                    "value": Field(
                        field_pb=fields["value"],
                        source_code_locations=self.source_code_locations,
                        proto_file_name=self.proto_file_name,
                        path=self.path,
                    ),
                }
        return map_entries

    @property
    def nested_enums(self) -> Dict[str, Enum]:
        """Return the nested enums in the message. Enum is identified by name."""
        # fmt: off
        return {
            enum.name: Enum(
                enum,
                self.proto_file_name,
                self.source_code_locations,
                # DescriptorProto.enum_type has field number 4.
                # So we append (4, nested_enum_index) to the path.
                self.path + (4, i),
            )
            for i, enum in enumerate(self.message_pb.enum_type)
        }
        # fmt: on

    @property
    def oneof_fields(self) -> Sequence[Field]:
        """Return the fields list that are in the oneof."""
        return [field for field in self.fields.values() if field.oneof]

    @property
    def resource(self) -> Optional[resource_pb2.ResourceDescriptor]:
        """If this message describes a resource, return the resource."""
        resource = self.message_pb.options.Extensions[resource_pb2.resource]
        if not resource.type or not resource.pattern:
            return None
        return WithLocation(
            resource,
            self.source_code_locations,
            # MessageOptions has field nnumber 7 and resource options
            # take the field number 1053.
            self.path + (7, 1053),
            self.proto_file_name,
        )

    @property
    def source_code_line(self):
        """Return the start line number of Message definition in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Method:
    """Description of a method (defined with the ``rpc`` keyword).

    method_pb: the descriptor of Method.
    messages_map: the map that contains all messages defined in the API definition files and
                  the dependencies. The key is message name, and value is the Message class.
    proto_file_name: the proto file where the Method exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the Method, by querying the above dictionary using the path,
          we can get the location information.
    """

    def __init__(
        self,
        method_pb: descriptor_pb2.MethodDescriptorProto,
        messages_map: Dict[str, Message],
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
    ):
        self.method_pb = method_pb
        self.messages_map = messages_map
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path

    @property
    def name(self):
        """Return the name of this method."""
        return self.method_pb.name

    @property
    def input(self):
        """Return the shortened input type of a method. We only need the name
        of the message to query in the messages_map.
        For example: `.example.v1.FooRequest` -> `FooRequest`
        """
        input_type = self.method_pb.input_type.rsplit(".", 1)[-1]
        # MethodDescriptorProto.input_type has field number 2
        return WithLocation(input_type, self.source_code_locations, self.path + (2,))

    @property
    def output(self):
        """Return the shortened output type of a method. We only need the name
        of the message to query in the messages_map.
        For example: `.example.v1.FooResponse` -> `FooResponse`

        If it is a longrunning method, just return `.google.longrunning.Operation`
        """
        output_type = (
            self.method_pb.output_type
            if self.longrunning
            else self.method_pb.output_type.rsplit(".", 1)[-1]
        )
        # MethodDescriptorProto.output_type has field number 3
        return WithLocation(output_type, self.source_code_locations, self.path + (3,))

    @property
    def longrunning(self) -> bool:
        """Return True if this is a longrunning method."""
        return self.method_pb.output_type.endswith(".google.longrunning.Operation")

    @property
    def client_streaming(self) -> bool:
        """Return True if this is a client-streamign method."""
        # MethodDescriptorProto.client_streaming has field number 5
        return WithLocation(
            self.method_pb.client_streaming,
            self.source_code_locations,
            self.path + (5,),
        )

    @property
    def server_streaming(self) -> bool:
        """Return True if this is a server-streaming method."""
        # MethodDescriptorProto.client_streaming has field number 6
        return WithLocation(
            self.method_pb.server_streaming,
            self.source_code_locations,
            self.path + (6,),
        )

    @property
    def paged_result_field(self) -> Optional[FieldDescriptorProto]:
        """Return the response pagination field if the method is paginated."""
        # (AIP 158) The response must not be a streaming response for a paginated method.
        if self.server_streaming.value:
            return None
        # If the output type is `google.longrunning.Operation`, the method is not paginated.
        if self.longrunning:
            return None
        if not self.messages_map or self.output.value not in self.messages_map:
            return None

        # API should provide a `string next_page_token` field in response messsage.
        # API should provide `int page_size` and `string page_token` fields in request message.
        # If the request field lacks any of the expected pagination fields,
        # then the method is not paginated.
        # Short message name e.g. .example.v1.FooRequest -> FooRequest
        response_message = self.messages_map[self.output.value]
        request_message = self.messages_map[self.input.value]
        response_fields_map = {f.name: f for f in response_message.fields.values()}
        request_fields_map = {f.name: f for f in request_message.fields.values()}

        for page_field in (
            (request_fields_map, "TYPE_INT32", "page_size"),
            (request_fields_map, "TYPE_STRING", "page_token"),
            (response_fields_map, "TYPE_STRING", "next_page_token"),
        ):
            field = page_field[0].get(page_field[2], None)
            if not field or field.proto_type.value != page_field[1]:
                return None

        # Return the first repeated field.
        # The field containing pagination results should be the first
        # field in the message and have a field number of 1.
        for field in response_fields_map.values():
            if field.repeated.value and field.number == 1:
                return field
        return None

    # fmt: off
    @property
    def lro_annotation(self):
        """Return the LRO operation_info annotation defined for this method."""
        # Skip the operations.proto because the `GetOperation` does not have LRO annotations.
        # Remove this condition will fail the service-annotation test in cli integration test.
        if not self.output.value.endswith("google.longrunning.Operation") or self.proto_file_name == "google/longrunning/operations.proto":
            return None
        op = self.method_pb.options.Extensions[operations_pb2.operation_info]
        if not op.response_type or not op.metadata_type:
            raise TypeError(
                f"rpc {self.name} returns a google.longrunning."
                "Operation, but is missing a response type or "
                "metadata type.",
            )
        lro_annotation = {
            "response_type": op.response_type,
            "metadata_type": op.metadata_type,
        }
        # MethodDescriptorProto.method_options has field number 4,
        # and MethodOptions.extensions[operation_info] has field number 1049.
        return WithLocation(
            lro_annotation,
            self.source_code_locations,
            self.path + (4, 1049),
        )

    @property
    def method_signatures(self) -> Optional[Sequence[str]]:
        """Return the signatures defined for this method."""
        signatures = self.method_pb.options.Extensions[client_pb2.method_signature]
        fields = [
            field.strip() for sig in signatures for field in sig.split(",") if field
        ]
        # MethodDescriptorProto.method_options has field number 4,
        # and MethodOptions.extensions[method_signature] has field number 1051.
        return WithLocation(
            fields,
            self.source_code_locations,
            self.path + (4, 1051, 0),
        )

    @property
    def http_annotation(self):
        """Return the http annotation defined for this method.
        The example return is:
        {'http_method': 'post', 'http_uri': '/v1/example:foo', 'http_body': '*'}

        return `None` if no http annotation exists.
        """
        http = self.method_pb.options.Extensions[annotations_pb2.http]
        potential_verbs = {
            "get": http.get,
            "put": http.put,
            "post": http.post,
            "delete": http.delete,
            "patch": http.patch,
            "custom": http.custom.path,
        }
        http_annotation = next(
            (
                {"http_method": verb, "http_uri": value, "http_body": http.body}
                for verb, value in potential_verbs.items()
                if value
            ),
            None,
        )
        # MethodDescriptorProto.method_options has field number 4,
        # and MethodOptions.extensions[http_annotation] has field number 72295728.
        return WithLocation(
            http_annotation,
            self.source_code_locations,
            self.path + (4, 72295728,)
        )
    # fmt: on

    @property
    def source_code_line(self):
        """Return the start line number of method definition in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Service:
    """Description of a service (defined with the ``service`` keyword).

    service_pb: the decriptor of service.
    messages_map: the map that contains all messages defined in the API definition files and
                  the dependencies. The key is message name, and value is the Message class.
    proto_file_name: the proto file where the Service exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the MethServiceod, by querying the above dictionary using the path,
          we can get the location information.
    api_version: the version of the API definition files.
    """

    def __init__(
        self,
        service_pb: descriptor_pb2.ServiceDescriptorProto,
        messages_map: Dict[str, Message],
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
        api_version: str = None,
    ):
        self.service_pb = service_pb
        self.messages_map = messages_map
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path
        self.api_version = api_version

    @property
    def name(self):
        """Return the name of the service."""
        return self.service_pb.name

    @property
    def methods(self) -> Dict[str, Method]:
        """Return the methods defined in the service. Method is identified by name."""
        # fmt: off
        return {
            method.name: Method(
                method,
                self.messages_map,
                self.proto_file_name,
                self.source_code_locations,
                # ServiceDescriptorProto.method has field number 2.
                # So we append (2, method_index) to the path.
                self.path + (2, i,),
            )
            for i, method in enumerate(self.service_pb.method)
        }
        # fmt: on

    @property
    def host(self) -> Optional[str]:
        """Return the hostname for this service, if specified.

        Returns:
            str: The hostname, with no protocol and no trailing ``/``.
        """
        if not self.service_pb.options.Extensions[client_pb2.default_host]:
            return None
        default_host = self.service_pb.options.Extensions[client_pb2.default_host]
        return WithLocation(
            value=default_host,
            source_code_locations=self.source_code_locations,
            # The ServiceOptions has field number 3, and default
            # host option has field number 1049.
            path=self.path + (3, 1049),
            proto_file_name=self.proto_file_name,
        )

    @property
    def oauth_scopes(self) -> Optional[Sequence[str]]:
        """Return a sequence of oauth scopes, if applicable.

        Returns:
            Sequence[str]: A sequence of OAuth scopes.
        """
        # fmt: off
        oauth_scopes = []
        for scope in self.service_pb.options.Extensions[client_pb2.oauth_scopes].split(","):
            if scope:
                oauth_scopes.append(
                    WithLocation(
                        scope.strip(),
                        self.source_code_locations,
                        self.path + (3, 1050),
                    )
                )

        return oauth_scopes
        # fmt: on

    @property
    def source_code_line(self):
        """Return the start line number of service definition in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class FileSet:
    """Description of a fileSet.

    file_set_pb: The FileDescriptorSet object that is obtained by proto compiler.
    """

    def __init__(
        self,
        file_set_pb: descriptor_pb2.FileDescriptorSet,
    ):
        # The default value for every language package option is a dict.
        # whose key is the option str, and value is the WithLocation object with
        # sourec code information.
        self.file_set_pb = file_set_pb
        # Create source code location map, key is the file name, value is the
        # source code information of every field.
        source_code_locations_map = self._get_source_code_locations_map()
        # Register all resources in the database.
        self.resources_database = self._get_resource_database(source_code_locations_map)
        # Get API version from definition files.
        self.api_version = self._get_api_version()
        # Get all messages in the map.
        self.messages_map = self._get_messages_map(source_code_locations_map)

        self.packaging_options_map = defaultdict(dict)
        self.services_map: Dict[str, Service] = {}
        self.enums_map: Dict[str, Enum] = {}
        path = ()
        for fd in file_set_pb.file:
            source_code_locations = source_code_locations_map[fd.name]
            # Create packaging options map and duplicate the per-language rules for namespaces.
            self._get_packaging_options_map(
                fd.options, fd.name, source_code_locations, path + (8,)
            )
            # fmt: off
            # FileDescriptorProto.service has field number 6
            self.services_map.update(
                (
                    service.name,
                    Service(
                        service,
                        self.messages_map,
                        fd.name,
                        source_code_locations,
                        path + (6, i,),
                        self.api_version,
                    ),
                )
                for i, service in enumerate(fd.service)
            )
            # FileDescriptorProto.service has field number 5
            self.enums_map.update(
                (
                    enum.name,
                    Enum(
                        enum,
                        fd.name,
                        source_code_locations,
                        path + (5, i,),
                    ),
                )
                for i, enum in enumerate(fd.enum_type)
            )
            # fmt: on

    def _get_messages_map(self, source_code_locations_map) -> Dict[str, Message]:
        messages_map: Dict[str, Message] = {}
        for fd in self.file_set_pb.file:
            source_code_locations = source_code_locations_map[fd.name]
            # FileDescriptorProto.message_type has field number 4.
            messages_map.update(
                (
                    message.name,
                    Message(
                        message,
                        fd.name,
                        source_code_locations,
                        (
                            4,
                            i,
                        ),
                        self.resources_database,
                        self.api_version,
                    ),
                )
                for i, message in enumerate(fd.message_type)
            )
        return messages_map

    def _get_api_version(self) -> Optional[str]:
        dependency_map: Dict[str, Sequence[str]] = defaultdict(list)
        for fd in self.file_set_pb.file:
            # Put the fileDescriptor and its dependencies to the dependency map.
            for dep in fd.dependency:
                dependency_map[dep].append(fd)
        # Find the root API definition file.
        version = r"(?P<version>v[0-9]+(p[0-9]+)?((alpha|beta)[0-9]*)?)"
        for f, deps in dependency_map.items():
            for dep in deps:
                if dep.name not in dependency_map:
                    match = re.search(version, dep.package)
                    return match.group() if match else None
        package = self.file_set_pb.file[0].package
        return re.search(version, package).group()

    def _get_source_code_locations_map(
        self,
    ) -> Dict[str, Dict[Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location]]:
        source_code_locations_map = {}
        for fd in self.file_set_pb.file:
            # Iterate over the source_code_info and place it into a dictionary.
            #
            # The comments in protocol buffers are sorted by a concept called
            # the "path", which is a sequence of integers described in more
            # detail below; this code simply shifts from a list to a dict,
            # with tuples of paths as the dictionary keys.
            source_code_locations = {
                tuple(location.path): location
                for location in fd.source_code_info.location
            }
            source_code_locations_map[fd.name] = source_code_locations
        return source_code_locations_map

    def _get_resource_database(
        self,
        source_code_locations_map: Dict[
            str, Dict[Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location]
        ],
    ):
        resources_database = ResourceDatabase()
        for fd in self.file_set_pb.file:
            source_code_locations = source_code_locations_map[fd.name]
            # Register file-level resource definitions in database.
            for i, resource in enumerate(
                fd.options.Extensions[resource_pb2.resource_definition]
            ):
                # The file option has field number 8, resource definition has
                # field number 1053, and the index of the resource should be
                # appended to the resource path.
                resource_path = (8, 1053, i)
                resources_database.register_resource(
                    WithLocation(
                        resource, source_code_locations, resource_path, fd.name
                    )
                )
            # Register message-level resource definitions in database.
            # Put first layer message in stack and iterate them for nested messages.
            message_stack = [
                # The messages in file has field number 4, the index of the messasge
                # should be appended to the resource path. Message option has field
                # number 7, and resource option has field number 1053.
                WithLocation(message, source_code_locations, (4, i, 7, 1053), fd.name)
                for i, message in enumerate(fd.message_type)
            ]

            while message_stack:
                message_with_location = message_stack.pop()
                message = message_with_location.value
                resource = message.options.Extensions[resource_pb2.resource]
                if resource.type and resource.pattern:
                    resources_database.register_resource(
                        WithLocation(
                            resource,
                            source_code_locations,
                            message_with_location.path,
                            fd.name,
                        )
                    )
                for i, nested_message in enumerate(message.nested_type):
                    # Nested message has field number 3, and index of the
                    # nested message is appended to the resource path.
                    # fmt: off
                    resource_path = message_with_location.path + (3,i,)
                    message_stack.append(
                        WithLocation(
                            nested_message,
                            source_code_locations,
                            resource_path,
                            fd.name,
                        )
                    )
                    # fmt: on

        return resources_database

    def _get_packaging_options_map(
        self,
        file_options: descriptor_pb2.FileOptions,
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
    ):
        # The minor version updates are allowed, for example
        # `java_package = "com.pubsub.v1"` is updated to `java_package = "com.pubsub.v1beta1".
        # But update between two stable versions (e.g. v1 to v2) is not permitted.
        packaging_options_path = {
            "java_package": (1,),
            "java_outer_classname": (8,),
            "csharp_namespace": (11,),
            "go_package": (37,),
            "swift_prefix": (39,),
            "php_namespace": (41,),
            "php_metadata_namespace": (44,),
            "php_class_prefix": (40,),
            "ruby_package": (45,),
        }
        # Put default empty set for every packaging options.
        for option in packaging_options_path.keys():
            if getattr(file_options, option) != "":
                self.packaging_options_map[option][
                    getattr(file_options, option)
                ] = WithLocation(
                    getattr(file_options, option),
                    source_code_locations,
                    path + packaging_options_path[option],
                    proto_file_name,
                )

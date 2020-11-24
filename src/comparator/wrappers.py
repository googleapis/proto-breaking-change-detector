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
        """Return the start line number of source code in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


@dataclasses.dataclass(frozen=True)
class Enum:
    """Description of an enum.

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
        # EnumDescriptorProto.value has field number 2.
        # So we append (2, value_index) to the path.
        return {
            enum_value.number: EnumValue(
                enum_value,
                self.proto_file_name,
                self.source_code_locations,
                self.path + (2, i),
            )
            for i, enum_value in enumerate(self.enum_pb.value)
        }

    @property
    def source_code_line(self):
        """Return the start line number of source code in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Field:
    """Description of a field.

    proto_file_name: the proto file where the Field exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the Field, by querying the above dictionary using the path,
          we can get the location information.
    """

    def __init__(
        self,
        field_pb: FieldDescriptorProto,
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
        file_resources: ResourceDatabase = None,
        message_resource: resource_pb2.ResourceDescriptor = None,
    ):
        """file_resources: file-level resource definitions.
        message_resource: message-level resource definition.

        We need the resource database information to determine if the resource_reference
        annotation removal or change is breaking or not.
        """
        self.field_pb = field_pb
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path
        self.file_resources = file_resources
        self.message_resource = message_resource

    def __getattr__(self, name):
        return getattr(self.field_pb, name)

    @property
    def name(self):
        return self.field_pb.name

    @property
    def number(self):
        """Return the number of the field."""
        return self.field_pb.number

    @property
    def label(self):
        """Return the label of the field.

        Returns:
            str: "LABEL_OPTIONAL", "LABEL_REPEATED" or "LABEL_REQUIRED".
        """
        # For proto3, only LABEL_REPEATED is explicitly specified which has a path.
        # For "LABEL_OPTIONAL" and "LABEL_REQUIRED", return the path of the field.
        label_repeated = (
            FieldDescriptorProto().Label.Name(self.field_pb.label) == "LABEL_REPEATED"
        )
        # FieldDescriptorProto.label has field number 4.
        return WithLocation(
            FieldDescriptorProto().Label.Name(self.field_pb.label),
            self.source_code_locations,
            self.path + (4,) if label_repeated else self.path,
        )

    @property
    def required(self) -> bool:
        """Return True if this field is required, False otherwise.

        Returns:
            bool: Whether this field is required in field_behavior annotation.
        """
        return (
            field_behavior_pb2.FieldBehavior.Value("REQUIRED")
            in self.field_pb.options.Extensions[field_behavior_pb2.field_behavior]
        )

    @property
    def proto_type(self):
        """Return the proto type constant e.g. `TYPE_ENUM`"""
        # FieldDescriptorProto.type has field number 5.
        return WithLocation(
            FieldDescriptorProto().Type.Name(self.field_pb.type),
            self.source_code_locations,
            self.path + (5,),
        )

    @property
    def is_primitive_type(self):
        """Return true if the proto _type is primitive python type like `TYPE_STRING`"""
        NON_PRIMITIVE_TYPE = ["TYPE_ENUM", "TYPE_MESSAGE", "TYPE_GROUP"]
        return False if self.proto_type.value in NON_PRIMITIVE_TYPE else True

    @property
    def type_name(self):
        """Return the type_name if the proto_type is not primitive, return `None` otherwise.
        For message and enum types, this is the name of the type like `.tutorial.example.Enum`"""
        # FieldDescriptorProto.type_name has field number 6.
        return (
            None
            if self.is_primitive_type
            else WithLocation(
                self.field_pb.type_name, self.source_code_locations, self.path + (6,)
            )
        )

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
        return WithLocation(resource_ref, self.source_code_locations, resource_ref_path)

    @property
    def child_type(self) -> bool:
        """Return True if the resource_reference has child_type, False otherwise"""
        resource_ref = self.field_pb.options.Extensions[resource_pb2.resource_reference]
        return True if len(resource_ref.child_type) > 0 else False

    @property
    def source_code_line(self):
        """Return the start line number of source code in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Message:
    """Description of a message (defined with the ``message`` keyword).

    proto_file_name: the proto file where the Message exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the Message, by querying the above dictionary using the path,
          we can get the location information.
    """

    def __init__(
        self,
        message_pb: descriptor_pb2.DescriptorProto,
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
        file_resources: ResourceDatabase = None,
    ):
        self.message_pb = message_pb
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path
        self.file_resources = file_resources

    def __getattr__(self, name):
        return getattr(self.message_pb, name)

    @property
    def name(self) -> str:
        return self.message_pb.name

    # fmt: off
    @property
    def fields(self) -> Dict[int, Field]:
        """Return fields in this message.

        Returns:
            Dict[int, Field]: Field is identified by number.
        """
        # DescriptorProto.field has field number 2.
        # So we append (2, field_index) to the path.
        return {
            field.number: Field(
                field,
                self.proto_file_name,
                self.source_code_locations,
                self.path + (2, i,),
                self.file_resources,
                self.resource,
            )
            for i, field in enumerate(self.message_pb.field)
        }

    @property
    def nested_messages(self) -> Dict[str, "Message"]:
        """Return the nested messsages in the message. Message is identified by name."""
        # DescriptorProto.nested_type has field number 3.
        # So we append (3, nested_message_index) to the path.
        return {
            message.name: Message(
                message,
                self.proto_file_name,
                self.source_code_locations,
                self.path + (3, i,),
                self.file_resources,
            )
            for i, message in enumerate(self.message_pb.nested_type)
        }

    @property
    def nested_enums(self) -> Dict[str, Enum]:
        """Return the nested enums in the message. Enum is identified by name."""
        # DescriptorProto.enum_type has field number 4.
        # So we append (4, nested_enum_index) to the path.
        return {
            enum.name: Enum(
                enum,
                self.proto_file_name,
                self.source_code_locations,
                self.path + (4, i,),
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
            self.path + (7, 1053),
            self.proto_file_name,
        )

    @property
    def source_code_line(self):
        """Return the start line number of source code in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Method:
    """Description of a method (defined with the ``rpc`` keyword).

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
            if field.label.value == "LABEL_REPEATED" and field.number == 1:
                return field
        return None

    # fmt: off
    @property
    def lro_annotation(self):
        """Return the LRO operation_info annotation defined for this method."""
        if not self.output.value.endswith("google.longrunning.Operation"):
            return None
        op = self.method_pb.options.Extensions[operations_pb2.operation_info]
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
        """Return the start line number of source code in the proto file."""
        return _get_source_code_line(self.source_code_locations, self.path)


class Service:
    """Description of a service (defined with the ``service`` keyword).

    proto_file_name: the proto file where the Service exists.
    source_code_locations: the dictionary that contains all the sourceCodeInfo in the fileDescriptorSet.
    path: the path to the MethServiceod, by querying the above dictionary using the path,
          we can get the location information.
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
    ):
        self.service_pb = service_pb
        self.messages_map = messages_map
        self.proto_file_name = proto_file_name
        self.source_code_locations = source_code_locations
        self.path = path

    @property
    def name(self):
        return self.service_pb.name

    @property
    def methods(self) -> Dict[str, Method]:
        """Return the methods defined in the service. Method is identified by name."""
        # ServiceDescriptorProto.method has field number 2.
        # So we append (2, method_index) to the path.
        # fmt: off
        return {
            method.name: Method(
                method,
                self.messages_map,
                self.proto_file_name,
                self.source_code_locations,
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
        if self.service_pb.options.Extensions[client_pb2.default_host]:
            return self.service_pb.options.Extensions[client_pb2.default_host]
        return ""

    @property
    def oauth_scopes(self) -> Optional[Sequence[str]]:
        """Return a sequence of oauth scopes, if applicable.

        Returns:
            Sequence[str]: A sequence of OAuth scopes.
        """
        # Return the OAuth scopes, split on comma.
        return tuple(
            i.strip()
            for i in self.service_pb.options.Extensions[client_pb2.oauth_scopes].split(
                ","
            )
            if i
        )

    @property
    def source_code_line(self):
        """Return the start line number of source code in the proto file."""
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
        self.packaging_options_map = defaultdict(dict)
        self.services_map: Dict[str, Service] = {}
        self.messages_map: Dict[str, Message] = {}
        self.enums_map: Dict[str, Enum] = {}
        self.resources_database = ResourceDatabase()
        dependency_map: Dict[str, Sequence[str]] = defaultdict(list)
        path = ()
        for fd in file_set_pb.file:
            # Put the fileDescriptor and its dependencies to the dependency map.
            for dep in fd.dependency:
                dependency_map[dep].append(fd)
            # Iterate over the source_code_info and place it into a dictionary.
            #
            # The comments in protocol buffers are sorted by a concept called
            # the "path", which is a sequence of integers described in more
            # detail below; this code simply shifts from a list to a dict,
            # with tuples of paths as the dictionary keys.
            source_code_locations: Dict[
                Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
            ] = {}
            for location in fd.source_code_info.location:
                source_code_locations[tuple(location.path)] = location
            # Create packaging options map and duplicate the per-language rules for namespaces.
            self._get_packaging_options_map(
                fd.options, fd.name, source_code_locations, path + (8,)
            )
            # fmt: off
            for i, resource in enumerate(
                fd.options.Extensions[resource_pb2.resource_definition]
            ):
                resource_path = path + (8, 1053, i)
                self.resources_database.register_resource(
                    WithLocation(resource, source_code_locations, resource_path, fd.name)
                )
            # FileDescriptorProto.message_type has field number 4
            self.messages_map.update(
                (
                    message.name,
                    Message(
                        message,
                        fd.name,
                        source_code_locations,
                        path + (4, i,),
                        self.resources_database,
                    ),
                )
                for i, message in enumerate(fd.message_type)
            )
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
        self.api_version = self._get_api_version(dependency_map)

    def _get_api_version(
        self, dependency_map: Dict[str, Sequence[str]]
    ) -> Optional[str]:
        # Find the root API definition file.
        version = r"(?P<version>v[0-9]+(p[0-9]+)?((alpha|beta)[0-9]*)?)"
        for f, deps in dependency_map.items():
            for dep in deps:
                if dep.name not in dependency_map:
                    match = re.search(version, dep.package)
                    return match.group() if match else None
        return None

    def _get_packaging_options_map(
        self,
        file_options: descriptor_pb2.FileOptions,
        proto_file_name: str,
        source_code_locations: Dict[
            Tuple[int, ...], descriptor_pb2.SourceCodeInfo.Location
        ],
        path: Tuple[int],
    ):
        # TODO(xiaozhenliu): check with One-platform about the version naming.
        # We should allow minor version updates, then the packaging options like
        # `java_package = "com.pubsub.v1"` will always be changed. But versions
        # update between two stable versions (e.g. v1 to v2) is not permitted.
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
            if hasattr(file_options, option):
                self.packaging_options_map[option][
                    getattr(file_options, option)
                ] = WithLocation(
                    getattr(file_options, option),
                    source_code_locations,
                    path + packaging_options_path[option],
                    proto_file_name,
                )

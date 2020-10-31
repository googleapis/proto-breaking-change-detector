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
from google.api import field_behavior_pb2
from google.api import resource_pb2
from google.api import client_pb2
from google.api import annotations_pb2
from google.longrunning import operations_pb2
from google.protobuf import descriptor_pb2
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from src.comparator.resource_database import ResourceDatabase
from typing import Dict, Sequence, Optional


@dataclasses.dataclass(frozen=True)
class EnumValue:
    """Description of an enum value."""

    enum_value_pb: descriptor_pb2.EnumValueDescriptorProto

    def __getattr__(self, name):
        return getattr(self.enum_value_pb, name)


@dataclasses.dataclass(frozen=True)
class Enum:
    """Description of an enum."""

    enum_pb: descriptor_pb2.EnumDescriptorProto

    def __getattr__(self, name):
        return getattr(self.enum_pb, name)

    @property
    def values(self) -> Dict[int, EnumValue]:
        """Return EnumValues in this Enum.

        Returns:
            Dict[int, EnumValue]: EnumValue is identified by number.
        """
        return {
            enum_value.number: EnumValue(enum_value)
            for enum_value in self.enum_pb.value
        }


class Field:
    """Description of an field."""

    def __init__(
        self,
        field_pb: FieldDescriptorProto,
        file_resources: ResourceDatabase = None,
        message_resource: resource_pb2.ResourceDescriptor = None,
    ):
        """file_resources: file-level resource definitions.
        message_resource: message-level resource definition.

        We need the resource database information to determine if the resource_reference
        annotation removal or change is breaking or not.
        """
        self.field_pb = field_pb
        self.file_resources = file_resources
        self.message_resource = message_resource

    @property
    def name(self):
        return self.field_pb.name

    @property
    def label(self):
        """Return the label of the field.

        Returns:
            str: "LABEL_OPTIONAL", "LABEL_REPEATED" or "LABEL_REQUIRED".
        """
        return FieldDescriptorProto().Label.Name(self.field_pb.label)

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
        return FieldDescriptorProto().Type.Name(self.field_pb.type)

    @property
    def oneof(self):
        """Return if the field is in oneof"""
        return self.field_pb.HasField("oneof_index")

    @property
    def resource_reference(self) -> Optional[resource_pb2.ResourceReference]:
        """Return the resource_reference annotation of the field if any"""
        resource_ref = self.field_pb.options.Extensions[resource_pb2.resource_reference]
        return resource_ref if resource_ref.type or resource_ref.child_type else None

    @property
    def child_type(self) -> bool:
        """Return True if the resource_reference has child_type, False otherwise"""
        resource_ref = self.field_pb.options.Extensions[resource_pb2.resource_reference]
        return True if len(resource_ref.child_type) > 0 else False


class Message:
    """Description of a message (defined with the ``message`` keyword)."""

    def __init__(
        self,
        message_pb: descriptor_pb2.DescriptorProto,
        file_resources: ResourceDatabase = None,
    ):
        self.message_pb = message_pb
        self.file_resources = file_resources

    @property
    def name(self) -> str:
        return self.message_pb.name

    @property
    def fields(self) -> Dict[int, Field]:
        """Return fields in this message.

        Returns:
            Dict[int, Field]: Field is identified by number.
        """
        return {
            field.number: Field(field, self.file_resources, self.resource)
            for field in self.message_pb.field
        }

    @property
    def nested_messages(self) -> Dict[str, "Message"]:
        """Return the nested messsages in the message. Message is identified by name."""
        return {
            message.name: Message(message, self.file_resources)
            for message in self.message_pb.nested_type
        }

    @property
    def nested_enums(self) -> Dict[str, Enum]:
        """Return the nested enums in the message. Enum is identified by name."""
        return {enum.name: Enum(enum) for enum in self.message_pb.enum_type}

    @property
    def oneof_fields(self) -> Sequence[Field]:
        """Return the fields list that are in the oneof."""
        return [field for field in self.fields.values() if field.oneof]

    @property
    def resource(self) -> Optional[resource_pb2.ResourceDescriptor]:
        """If this message describes a resource, return the resource."""
        resource = self.message_pb.options.Extensions[resource_pb2.resource]
        return resource if resource.type and resource.pattern else None


class Method:
    """Description of a method (defined with the ``rpc`` keyword)."""

    def __init__(
        self,
        method_pb: descriptor_pb2.MethodDescriptorProto,
        messages_map: Dict[str, Message],
    ):
        self.method_pb = method_pb
        self.messages_map = messages_map

    @property
    def name(self):
        return self.method_pb.name

    @property
    def input(self):
        """Return the shortened input type of a method. We only need the name
        of the message to query in the messages_map.
        For example: `.example.v1.FooRequest` -> `FooRequest`
        """
        return self.method_pb.input_type.rsplit(".", 1)[-1]

    @property
    def output(self):
        """Return the shortened output type of a method. We only need the name
        of the message to query in the messages_map.
        For example: `.example.v1.FooResponse` -> `FooResponse`

        If it is a longrunning method, just return `.google.longrunning.Operation`
        """
        if self.method_pb.output_type.endswith(".google.longrunning.Operation"):
            return self.method_pb.output_type
        return self.method_pb.output_type.rsplit(".", 1)[-1]

    @property
    def paged_result_field(self) -> Optional[FieldDescriptorProto]:
        """Return the response pagination field if the method is paginated."""
        # (AIP 158) The response must not be a streaming response for a paginated method.
        if self.method_pb.server_streaming:
            return None
        # If the output type is `google.longrunning.Operation`, the method is not paginated.
        if self.method_pb.output_type.endswith("google.longrunning.Operation"):
            return None
        # API should provide a `string next_page_token` field in response messsage.
        # API should provide `int page_size` and `string page_token` fields in request message.
        # If the request field lacks any of the expected pagination fields,
        # then the method is not paginated.
        # Short message name e.g. .example.v1.FooRequest -> FooRequest
        response_message = self.messages_map[self.output]
        request_message = self.messages_map[self.input]
        response_fields_map = {f.name: f for f in response_message.fields.values()}
        request_fields_map = {f.name: f for f in request_message.fields.values()}

        for page_field in (
            (request_fields_map, "TYPE_INT32", "page_size"),
            (request_fields_map, "TYPE_STRING", "page_token"),
            (response_fields_map, "TYPE_STRING", "next_page_token"),
        ):
            field = page_field[0].get(page_field[2], None)
            if not field or field.type != page_field[1]:
                return None

        # Return the first repeated field.
        # The field containing pagination results should be the first
        # field in the message and have a field number of 1.
        for field in response_fields_map.values():
            if field.label == "LABEL_REPEATED" and field.number == 1:
                return field
        return None

    @property
    def lro(self):
        """Return the LRO operation_info annotation defined for this method."""
        if not self.output.endswith("google.longrunning.Operation"):
            return None
        op = self.method_pb.options.Extensions[operations_pb2.operation_info]
        if not op.response_type or not op.metadata_type:
            raise TypeError(
                f"rpc {self.name} returns a google.longrunning."
                "Operation, but is missing a response type or "
                "metadata type.",
            )
        return {
            "response_type": op.response_type,
            "metadata_type": op.metadata_type,
        }

    @property
    def method_signatures(self) -> Optional[Sequence[str]]:
        """Return the signature defined for this method."""
        signatures = self.method_pb.options.Extensions[client_pb2.method_signature]
        fields = [
            field.strip() for sig in signatures for field in sig.split(",") if field
        ]
        return fields

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
        return next(
            (
                {"http_method": verb, "http_uri": value, "http_body": http.body}
                for verb, value in potential_verbs.items()
                if value
            ),
            None,
        )


class Service:
    """Description of a service (defined with the ``service`` keyword)."""

    def __init__(
        self,
        service_pb: descriptor_pb2.ServiceDescriptorProto,
        messages_map: Dict[str, Message],
    ):
        self.service_pb = service_pb
        self.messages_map = messages_map

    @property
    def name(self):
        return self.service_pb.name

    @property
    def methods(self) -> Dict[str, Method]:
        """Return the methods defined in the service. Method is identified by name."""
        return {
            method.name: Method(method, self.messages_map)
            for method in self.service_pb.method
        }

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


class FileSet:
    """Description of a fileSet."""

    def __init__(self, file_set_pb: descriptor_pb2.FileDescriptorSet):
        self.packaging_options_map = {}
        self.services_map: Dict[str, Service] = {}
        self.messages_map: Dict[str, Message] = {}
        self.enums_map: Dict[str, Enum] = {}
        self.resources_database = ResourceDatabase()
        for fd in file_set_pb.file:
            # Create packaging options map and duplicate the per-language rules for namespaces.
            self.packaging_options_map = self._get_packaging_options_map(fd.options)
            for resource in fd.options.Extensions[resource_pb2.resource_definition]:
                self.resources_database.register_resource(resource)
            self.messages_map.update(
                (message.name, Message(message, self.resources_database))
                for message in fd.message_type
            )
            self.services_map.update(
                (service.name, Service(service, self.messages_map))
                for service in fd.service
            )
            self.enums_map.update((enum.name, Enum(enum)) for enum in fd.enum_type)

    def _get_packaging_options_map(self, file_options: descriptor_pb2.FileOptions):
        # TODO(xiaozhenliu): check with One-platform about the version naming.
        # We should allow minor version updates, then the packaging options like
        # `java_package = "com.pubsub.v1"` will always be changed. But versions
        # updates between two stable versions (e.g. v1 to v2) is not permitted.
        pass

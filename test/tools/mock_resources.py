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

from proto_bcd.comparator.resource_database import ResourceDatabase
from proto_bcd.comparator.wrappers import WithLocation
from google.protobuf import descriptor_pb2 as desc
from google.api import resource_pb2


def make_resource_database(resources):
    resource_database = ResourceDatabase()
    for resource in resources:
        resource_database.register_resource(resource)
    return resource_database


def make_file_options_resource_definition(
    resource_type: str, resource_patterns: [str]
) -> desc.FileOptions:
    file_options = desc.FileOptions()
    file_options.Extensions[resource_pb2.resource_definition].append(
        resource_pb2.ResourceDescriptor(
            type=resource_type,
            pattern=resource_patterns,
        )
    )
    return file_options


def make_message_options_resource_definition(
    resource_type: str, resource_patterns: [str]
) -> desc.MessageOptions:
    message_options = desc.MessageOptions()
    resource = message_options.Extensions[resource_pb2.resource]
    resource.type = resource_type
    resource.pattern.extend(resource_patterns)
    return message_options


def make_field_annotation_resource_reference(resource_type: str, is_child_type: bool):
    field_options = desc.FieldOptions()
    if is_child_type:
        field_options.Extensions[resource_pb2.resource_reference].child_type = (
            resource_type
        )
    else:
        field_options.Extensions[resource_pb2.resource_reference].type = resource_type
    return field_options


def make_resource_descriptor(
    resource_type: str, resource_patterns: [str]
) -> resource_pb2.ResourceDescriptor:
    resource_descriptor = resource_pb2.ResourceDescriptor(
        type=resource_type, pattern=list(resource_patterns)
    )
    return WithLocation(resource_descriptor, None, None)

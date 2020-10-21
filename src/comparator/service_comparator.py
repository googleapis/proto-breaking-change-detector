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

from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.descriptor_pb2 import DescriptorProto
from google.protobuf.descriptor_pb2 import MethodDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory
from typing import Dict, Optional


class ServiceComparator:
    def __init__(
        self,
        service_original: ServiceDescriptorProto,
        service_update: ServiceDescriptorProto,
        messages_map_original: Dict[str, DescriptorProto],
        messages_map_update: Dict[str, DescriptorProto],
    ):
        self.service_original = service_original
        self.service_update = service_update
        self.messages_map_original = messages_map_original
        self.messages_map_update = messages_map_update

    def compare(self):
        # 1. If original service is None, then a new service is added.
        if self.service_original is None:
            msg = f"A new service {self.service_update.name} is added."
            FindingContainer.addFinding(
                FindingCategory.SERVICE_ADDITION, "", msg, False
            )
            return
        # 2. If updated service is None, then the original service is removed.
        if self.service_update is None:
            msg = f"A service {self.service_original.name} is removed"
            FindingContainer.addFinding(FindingCategory.SERVICE_REMOVAL, "", msg, True)
            return

        # 3. TODO(xiaozhenliu): method_signature annotation
        # 4. TODO(xiaozhenliu): LRO operation_info annotation
        # 5. TODO(xiaozhenliu): google.api.http annotation
        # 6. Check the methods list
        self._compareRpcMethods(
            self.service_original,
            self.service_update,
            self.messages_map_original,
            self.messages_map_update,
        )

    def _compareRpcMethods(
        self,
        service_original,
        service_update,
        messages_map_original,
        messages_map_update,
    ):
        methods_original = {x.name: x for x in service_original.method}
        methods_update = {x.name: x for x in service_update.method}
        methods_original_keys = set(methods_original.keys())
        methods_update_keys = set(methods_update.keys())
        # 6.1 An RPC method is removed.
        for name in methods_original_keys - methods_update_keys:
            msg = f"An rpc method {name} is removed"
            FindingContainer.addFinding(FindingCategory.METHOD_REMOVAL, "", msg, True)
        # 6.2 An RPC method is added.
        for name in methods_update_keys - methods_original_keys:
            msg = f"An rpc method {name} is added"
            FindingContainer.addFinding(FindingCategory.METHOD_ADDTION, "", msg, False)
        for name in methods_update_keys & methods_original_keys:
            method_original = methods_original[name]
            method_update = methods_update[name]
            # 6.3 The request type of an RPC method is changed.
            input_type_original = method_original.input_type.rsplit(".", 1)[-1]
            input_type_update = method_update.input_type.rsplit(".", 1)[-1]
            if input_type_original != input_type_update:
                msg = f"Input type of method {name} is changed from {input_type_original} to {input_type_update}"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_INPUT_TYPE_CHANGE, "", msg, True
                )
            # 6.4 The request type of an RPC method is changed.
            # We use short message name `FooRequest` instead of `.example.v1.FooRequest`
            # because the package name will always be updated e.g `.example.v1beta1.FooRequest`
            response_type_original = method_original.output_type.rsplit(".", 1)[-1]
            response_type_update = method_update.output_type.rsplit(".", 1)[-1]
            if response_type_original != response_type_update:
                msg = f"Output type of method {name} is changed from {response_type_original} to {response_type_update}"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_RESPONSE_TYPE_CHANGE, "", msg, True
                )
            # 6.5 The request streaming state of an RPC method is changed.
            if method_original.client_streaming != method_update.client_streaming:
                msg = f"The request streaming type of method {name} is changed"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_CLIENT_STREAMING_CHANGE, "", msg, True
                )
            # 6.6 The response streaming state of an RPC method is changed.
            if method_original.server_streaming != method_update.server_streaming:
                msg = f"The response streaming type of method {name} is changed"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_SERVER_STREAMING_CHANGE, "", msg, True
                )
            # 6.7 The paginated response of an RPC method is changed.
            if self._paged_result_field(
                method_original, messages_map_original
            ) != self._paged_result_field(method_update, messages_map_update):
                msg = f"The paginated response of method {name} is changed"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE, "", msg, True
                )

    def _paged_result_field(
        self, method: MethodDescriptorProto, messages_map: Dict[str, DescriptorProto]
    ) -> Optional[FieldDescriptorProto]:
        """Return the response pagination field if the method is paginated."""
        # (AIP 158) The response must not be a streaming response for a paginated method.
        if method.server_streaming:
            return None
        # API should provide a `string next_page_token` field in response messsage.
        # API should provide `int page_size` and `string page_token` fields in request message.
        # If the request field lacks any of the expected pagination fields,
        # then the method is not paginated.
        # Short message name e.g. .example.v1.FooRequest -> FooRequest
        response_message = messages_map[method.output_type.rsplit(".", 1)[-1]]
        request_message = messages_map[method.input_type.rsplit(".", 1)[-1]]
        response_fields_map = {f.name: f for f in response_message.field}
        request_fields_map = {f.name: f for f in request_message.field}

        for page_field in (
            (request_fields_map, "TYPE_INT32", "page_size"),
            (request_fields_map, "TYPE_STRING", "page_token"),
            (response_fields_map, "TYPE_STRING", "next_page_token"),
        ):
            field = page_field[0].get(page_field[2], None)
            if (
                not field
                or FieldDescriptorProto().Type.Name(field.type) != page_field[1]
            ):
                return None

        # Return the first repeated field.
        # The field containing pagination results should be the first
        # field in the message and have a field number of 1.
        for field in response_fields_map.values():
            if (
                FieldDescriptorProto().Label.Name(field.label) == "LABEL_REPEATED"
                and field.number == 1
            ):
                return field
        return None

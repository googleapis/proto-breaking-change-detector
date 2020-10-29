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
from google.api import client_pb2
from google.api import annotations_pb2
from google.longrunning import operations_pb2
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
        # 3. Check the methods list
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
        # 3.1 An RPC method is removed.
        for name in methods_original_keys - methods_update_keys:
            msg = f"An rpc method {name} is removed"
            FindingContainer.addFinding(FindingCategory.METHOD_REMOVAL, "", msg, True)
        # 3.2 An RPC method is added.
        for name in methods_update_keys - methods_original_keys:
            msg = f"An rpc method {name} is added"
            FindingContainer.addFinding(FindingCategory.METHOD_ADDTION, "", msg, False)
        for name in methods_update_keys & methods_original_keys:
            method_original = methods_original[name]
            method_update = methods_update[name]
            # 3.3 The request type of an RPC method is changed.
            input_type_original = method_original.input_type.rsplit(".", 1)[-1]
            input_type_update = method_update.input_type.rsplit(".", 1)[-1]
            if input_type_original != input_type_update:
                msg = f"Input type of method {name} is changed from {input_type_original} to {input_type_update}"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_INPUT_TYPE_CHANGE, "", msg, True
                )
            # 3.4 The response type of an RPC method is changed.
            # We use short message name `FooRequest` instead of `.example.v1.FooRequest`
            # because the package name will always be updated e.g `.example.v1beta1.FooRequest`
            response_type_original = method_original.output_type.rsplit(".", 1)[-1]
            response_type_update = method_update.output_type.rsplit(".", 1)[-1]
            if response_type_original != response_type_update:
                msg = f"Output type of method {name} is changed from {response_type_original} to {response_type_update}"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_RESPONSE_TYPE_CHANGE, "", msg, True
                )
            # 3.5 The request streaming state of an RPC method is changed.
            if method_original.client_streaming != method_update.client_streaming:
                msg = f"The request streaming type of method {name} is changed"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_CLIENT_STREAMING_CHANGE, "", msg, True
                )
            # 3.6 The response streaming state of an RPC method is changed.
            if method_original.server_streaming != method_update.server_streaming:
                msg = f"The response streaming type of method {name} is changed"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_SERVER_STREAMING_CHANGE, "", msg, True
                )
            # 3.7 The paginated response of an RPC method is changed.
            if self._paged_result_field(
                method_original, messages_map_original
            ) != self._paged_result_field(method_update, messages_map_update):
                msg = f"The paginated response of method {name} is changed"
                FindingContainer.addFinding(
                    FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE, "", msg, True
                )
            # 3.8 The method_signature annotation is changed.
            signatures_original = self._get_signatures(method_original)
            signatures_update = self._get_signatures(method_update)
            self._compare_method_signatures(signatures_original, signatures_update)

            # 3.9 The LRO operation_info annotation is changed.
            lro_original = self._get_lro(method_original)
            lro_update = self._get_lro(method_update)
            self._compare_lro_annotations(lro_original, lro_update)

            # 3.10 The google.api.http annotation is changed.
            http_annotation_original = self._get_http_annotation(method_original)
            http_annotation_update = self._get_http_annotation(method_update)
            self._compare_http_annotation(
                http_annotation_original, http_annotation_update
            )

    def _get_http_annotation(self, method: MethodDescriptorProto):
        # Return the http annotation defined for this method.
        # The example return is {'http_method': 'post', 'http_uri': '/v1/example:foo', 'http_body': '*'}
        # return `None` if no http annotation exists.
        http = method.options.Extensions[annotations_pb2.http]
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

    def _compare_http_annotation(
        self, http_annotation_original, http_annotation_update
    ):
        """Compare the fields `http_method, http_uri, http_body` of google.api.http annotation."""
        if not http_annotation_original or not http_annotation_update:
            # (Aip127) APIs must provide HTTP definitions for each RPC that they define,
            # except for bi-directional streaming RPCs, so the http_annotation addition/removal indicates
            # streaming state changes of the RPC, which is a breaking change.
            if http_annotation_original and not http_annotation_update:
                FindingContainer.addFinding(
                    FindingCategory.HTTP_ANNOTATION_REMOVAL,
                    "",
                    "A google.api.http annotation is removed.",
                    False,
                )
            if not http_annotation_original and http_annotation_update:
                FindingContainer.addFinding(
                    FindingCategory.HTTP_ANNOTATION_ADDITION,
                    "",
                    "A google.api.http annotation is added.",
                    False,
                )
            return
        for annotation in (
            ("http_method", "None", "An existing http method is changed."),
            ("http_uri", "None", "An existing http method URI is changed."),
            ("http_body", "None", "An existing http method body is changed."),
        ):
            # TODO (xiaozhenliu): this should allow version updates. For example,
            # from `v1/example:foo` to `v1beta1/example:foo` is not a breaking change.
            if http_annotation_original.get(
                annotation[0], annotation[1]
            ) != http_annotation_update.get(annotation[0], annotation[1]):
                FindingContainer.addFinding(
                    FindingCategory.HTTP_ANNOTATION_CHANGE,
                    "",
                    annotation[2],
                    True,
                )

    def _get_lro(self, method: MethodDescriptorProto):
        """Return the LRO operation_info annotation defined for this method."""
        if not method.output_type.endswith("google.longrunning.Operation"):
            return None
        op = method.options.Extensions[operations_pb2.operation_info]
        if not op.response_type or not op.metadata_type:
            raise TypeError(
                f"rpc {method.name} returns a google.longrunning."
                "Operation, but is missing a response type or "
                "metadata type.",
            )
        return {"response_type": op.response_type, "metadata_type": op.metadata_type}

    def _compare_lro_annotations(self, lro_original, lro_update):
        if not lro_original or not lro_update:
            # LRO operation_info annotation addition.
            if not lro_original and lro_update:
                FindingContainer.addFinding(
                    FindingCategory.LRO_ANNOTATION_ADDITION,
                    "",
                    "A LRO operation_info annotation is added.",
                    False,
                )
            # LRO operation_info annotation removal.
            if lro_original and not lro_update:
                FindingContainer.addFinding(
                    FindingCategory.LRO_ANNOTATION_REMOVAL,
                    "",
                    "A LRO operation_info annotation is removed.",
                    False,
                )
            return
        # The response_type value of LRO operation_info is changed.
        if lro_original["response_type"] != lro_update["response_type"]:
            FindingContainer.addFinding(
                FindingCategory.LRO_RESPONSE_CHANGE,
                "",
                f"The response_type of LRO operation_info annotation is changed from {lro_original['response_type']} to {lro_update['response_type']}",
                True,
            )
        # The metadata_type value of LRO operation_info is changed.
        if lro_original["metadata_type"] != lro_update["metadata_type"]:
            FindingContainer.addFinding(
                FindingCategory.LRO_METADATA_CHANGE,
                "",
                f"The metadata_type of LRO operation_info annotation is changed from {lro_original['metadata_type']} to {lro_update['metadata_type']}",
                True,
            )

    def _get_signatures(self, method: MethodDescriptorProto):
        """Return the signature defined for this method."""
        return method.options.Extensions[client_pb2.method_signature]

    def _compare_method_signatures(self, signatures_original, signatures_update):
        def _filter_fields(signatures):
            fields = [
                field.strip() for sig in signatures for field in sig.split(",") if field
            ]
            return fields

        # Flatten the method_signatures fields.
        # For example: ['content, error'] to ['content', 'error']
        fields_original = _filter_fields(signatures_original)
        fields_update = _filter_fields(signatures_update)
        if len(fields_original) > len(fields_update):
            FindingContainer.addFinding(
                FindingCategory.METHOD_SIGNATURE_CHANGE,
                "",
                "An existing method_signature is removed.",
                True,
            )
        for old_sig, new_sig in zip(fields_original, fields_update):
            if old_sig != new_sig:
                FindingContainer.addFinding(
                    FindingCategory.METHOD_SIGNATURE_CHANGE,
                    "",
                    f"An existing method_signature is changed from '{old_sig}' to '{new_sig}'.",
                    True,
                )

    def _paged_result_field(
        self, method: MethodDescriptorProto, messages_map: Dict[str, DescriptorProto]
    ) -> Optional[FieldDescriptorProto]:
        """Return the response pagination field if the method is paginated."""
        # (AIP 158) The response must not be a streaming response for a paginated method.
        if method.server_streaming:
            return None
        # If the output type is `google.longrunning.Operation`, the method is not paginated.
        if method.output_type.endswith("google.longrunning.Operation"):
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

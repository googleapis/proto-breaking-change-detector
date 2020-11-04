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

from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory
from src.comparator.wrappers import Service

from typing import Dict, Optional


class ServiceComparator:
    def __init__(
        self,
        service_original: Service,
        service_update: Service,
    ):
        self.service_original = service_original
        self.service_update = service_update

    def compare(self):
        # 1. If original service is None, then a new service is added.
        if self.service_original is None:
            FindingContainer.addFinding(
                category=FindingCategory.SERVICE_ADDITION,
                location=f"{self.service_update.proto_file_name} Line: {self.service_update.source_code_line}",
                message=f"A new service {self.service_update.name} is added.",
                actionable=False,
            )
            return
        # 2. If updated service is None, then the original service is removed.
        if self.service_update is None:
            FindingContainer.addFinding(
                category=FindingCategory.SERVICE_REMOVAL,
                location=f"{self.service_original.proto_file_name} Line: {self.service_original.source_code_line}",
                message=f"A service {self.service_original.name} is removed",
                actionable=True,
            )
            return
        self.messages_map_original = self.service_original.messages_map
        self.messages_map_update = self.service_update.messages_map
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
        methods_original = service_original.methods
        methods_update = service_update.methods
        methods_original_keys = set(methods_original.keys())
        methods_update_keys = set(methods_update.keys())
        # 3.1 An RPC method is removed.
        for name in methods_original_keys - methods_update_keys:
            removed_method = methods_original[name]
            FindingContainer.addFinding(
                category=FindingCategory.METHOD_REMOVAL,
                location=f"{removed_method.proto_file_name} Line: {removed_method.source_code_line}",
                message=f"An rpc method {name} is removed",
                actionable=True,
            )
        # 3.2 An RPC method is added.
        for name in methods_update_keys - methods_original_keys:
            added_method = methods_update[name]
            FindingContainer.addFinding(
                category=FindingCategory.METHOD_ADDTION,
                location=f"{added_method.proto_file_name} Line: {added_method.source_code_line}",
                message=f"An rpc method {name} is added",
                actionable=False,
            )
        for name in methods_update_keys & methods_original_keys:
            method_original = methods_original[name]
            method_update = methods_update[name]
            # 3.3 The request type of an RPC method is changed.
            input_type_original = method_original.input.value
            input_type_update = method_update.input.value
            if input_type_original != input_type_update:
                FindingContainer.addFinding(
                    category=FindingCategory.METHOD_INPUT_TYPE_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.input.source_code_line}",
                    message=f"Input type of method {name} is changed from {input_type_original} to {input_type_update}",
                    actionable=True,
                )
            # 3.4 The response type of an RPC method is changed.
            response_type_original = method_original.output.value
            response_type_update = method_update.output.value
            if response_type_original != response_type_update:
                FindingContainer.addFinding(
                    category=FindingCategory.METHOD_RESPONSE_TYPE_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.output.source_code_line}",
                    message=f"Output type of method {name} is changed from {response_type_original} to {response_type_update}",
                    actionable=True,
                )
            # 3.5 The request streaming state of an RPC method is changed.
            if (
                method_original.client_streaming.value
                != method_update.client_streaming.value
            ):
                FindingContainer.addFinding(
                    category=FindingCategory.METHOD_CLIENT_STREAMING_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.client_streaming.source_code_line}",
                    message=f"The request streaming type of method {name} is changed",
                    actionable=True,
                )
            # 3.6 The response streaming state of an RPC method is changed.
            if (
                method_original.server_streaming.value
                != method_update.server_streaming.value
            ):
                FindingContainer.addFinding(
                    category=FindingCategory.METHOD_SERVER_STREAMING_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.server_streaming.source_code_line}",
                    message=f"The response streaming type of method {name} is changed",
                    actionable=True,
                )
            # 3.7 The paginated response of an RPC method is changed.
            if method_original.paged_result_field != method_update.paged_result_field:
                FindingContainer.addFinding(
                    category=FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.source_code_line}",
                    message=f"The paginated response of method {name} is changed",
                    actionable=True,
                )
            # The customized annotation options share the same field number (1000)
            # in MethodDescriptorProto.options.
            # 3.8 The method_signature annotation is changed.
            self._compare_method_signatures(method_original, method_update)

            # 3.9 The LRO operation_info annotation is changed.
            self._compare_lro_annotations(method_original, method_update)

            # 3.10 The google.api.http annotation is changed.
            self._compare_http_annotation(method_original, method_update)

    def _compare_http_annotation(self, method_original, method_update):
        """Compare the fields `http_method, http_uri, http_body` of google.api.http annotation."""
        http_annotation_original = method_original.http_annotation.value
        http_annotation_update = method_update.http_annotation.value

        if not http_annotation_original or not http_annotation_update:
            # (Aip127) APIs must provide HTTP definitions for each RPC that they define,
            # except for bi-directional streaming RPCs, so the http_annotation addition/removal indicates
            # streaming state changes of the RPC, which is a breaking change.
            if http_annotation_original and not http_annotation_update:
                FindingContainer.addFinding(
                    category=FindingCategory.HTTP_ANNOTATION_REMOVAL,
                    location=f"{method_original.proto_file_name} Line: {method_original.http_annotation.source_code_line}",
                    message="A google.api.http annotation is removed.",
                    actionable=True,
                )
            if not http_annotation_original and http_annotation_update:
                FindingContainer.addFinding(
                    category=FindingCategory.HTTP_ANNOTATION_ADDITION,
                    location=f"{method_update.proto_file_name} Line: {method_update.http_annotation.source_code_line}",
                    message="A google.api.http annotation is added.",
                    actionable=False,
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
                    category=FindingCategory.HTTP_ANNOTATION_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.http_annotation.source_code_line}",
                    message=annotation[2],
                    actionable=True,
                )

    def _compare_lro_annotations(self, method_original, method_update):
        lro_original = method_original.lro_annotation
        lro_update = method_update.lro_annotation
        if not lro_original and not lro_update:
            return
        # LRO operation_info annotation addition.
        if not lro_original and lro_update:
            FindingContainer.addFinding(
                category=FindingCategory.LRO_ANNOTATION_ADDITION,
                location=f"{method_update.proto_file_name} Line: {method_update.lro_annotation.source_code_line}",
                message="A LRO operation_info annotation is added.",
                actionable=False,
            )
            return
        # LRO operation_info annotation removal.
        if lro_original and not lro_update:
            FindingContainer.addFinding(
                category=FindingCategory.LRO_ANNOTATION_REMOVAL,
                location=f"{method_original.proto_file_name} Line: {method_original.lro_annotation.source_code_line}",
                message="A LRO operation_info annotation is removed.",
                actionable=False,
            )
            return
        # The response_type value of LRO operation_info is changed.
        if lro_original.value["response_type"] != lro_update.value["response_type"]:
            FindingContainer.addFinding(
                category=FindingCategory.LRO_RESPONSE_CHANGE,
                location=f"{method_update.proto_file_name} Line: {lro_update.source_code_line}",
                message=f"The response_type of LRO operation_info annotation is changed from {lro_original.value['response_type']} to {lro_update.value['response_type']}",
                actionable=True,
            )
        # The metadata_type value of LRO operation_info is changed.
        if lro_original.value["metadata_type"] != lro_update.value["metadata_type"]:
            FindingContainer.addFinding(
                category=FindingCategory.LRO_METADATA_CHANGE,
                location=f"{method_update.proto_file_name} Line: {lro_update.source_code_line}",
                message=f"The metadata_type of LRO operation_info annotation is changed from {lro_original.value['metadata_type']} to {lro_update.value['metadata_type']}",
                actionable=True,
            )

    def _compare_method_signatures(self, method_original, method_update):
        signatures_original = method_original.method_signatures.value
        signatures_update = method_update.method_signatures.value
        if len(signatures_original) > len(signatures_update):
            FindingContainer.addFinding(
                category=FindingCategory.METHOD_SIGNATURE_CHANGE,
                location=f"{method_original.proto_file_name} Line: {method_original.method_signatures.source_code_line}",
                message="An existing method_signature is removed.",
                actionable=True,
            )
        for old_sig, new_sig in zip(signatures_original, signatures_update):
            if old_sig != new_sig:
                FindingContainer.addFinding(
                    category=FindingCategory.METHOD_SIGNATURE_CHANGE,
                    location=f"{method_update.proto_file_name} Line: {method_update.method_signatures.source_code_line}",
                    message=f"An existing method_signature is changed from '{old_sig}' to '{new_sig}'.",
                    actionable=True,
                )

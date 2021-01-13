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
from src.findings.utils import FindingCategory, ChangeType
from src.comparator.wrappers import Service


class ServiceComparator:
    def __init__(
        self,
        service_original: Service,
        service_update: Service,
        finding_container: FindingContainer,
    ):
        self.service_original = service_original
        self.service_update = service_update
        self.finding_container = finding_container

    def compare(self):
        # 1. If original service is None, then a new service is added.
        if self.service_original is None:
            self.finding_container.addFinding(
                category=FindingCategory.SERVICE_ADDITION,
                proto_file_name=self.service_update.proto_file_name,
                source_code_line=self.service_update.source_code_line,
                message=f"A new service `{self.service_update.name}` is added.",
                change_type=ChangeType.MINOR,
            )
            return
        # 2. If updated service is None, then the original service is removed.
        if self.service_update is None:
            self.finding_container.addFinding(
                category=FindingCategory.SERVICE_REMOVAL,
                proto_file_name=self.service_original.proto_file_name,
                source_code_line=self.service_original.source_code_line,
                message=f"An existing service `{self.service_original.name}` is removed.",
                change_type=ChangeType.MAJOR,
            )
            return
        # 3. Check the default host.
        self._compare_host()
        # 4. Check the oauth scopes list.
        self._compare_oauth_scopes()
        # 5. Check the methods list
        self._compareRpcMethods()

    def _compare_host(self):
        if not self.service_original.host and not self.service_update.host:
            return
        if not self.service_original.host:
            host = self.service_update.host
            self.finding_container.addFinding(
                category=FindingCategory.SERVICE_HOST_ADDITION,
                proto_file_name=host.proto_file_name,
                source_code_line=host.source_code_line,
                message=f"A new default host `{host.value}` is added.",
                change_type=ChangeType.MINOR,
            )
            return
        if not self.service_update.host:
            host = self.service_original.host
            self.finding_container.addFinding(
                category=FindingCategory.SERVICE_HOST_REMOVAL,
                proto_file_name=host.proto_file_name,
                source_code_line=host.source_code_line,
                message=f"An existing default host `{host.value}` is removed.",
                change_type=ChangeType.MAJOR,
            )
            return
        host_original = self.service_original.host
        host_update = self.service_update.host
        if host_original.value != host_update.value:
            self.finding_container.addFinding(
                category=FindingCategory.SERVICE_HOST_CHANGE,
                proto_file_name=host_update.proto_file_name,
                source_code_line=host_update.source_code_line,
                message=f"An existing default host is updated from `{host_original.value}` to `{host_update.value}`.",
                change_type=ChangeType.MAJOR,
            )

    def _compare_oauth_scopes(self):
        oauth_scopes_original = {
            scope.value: scope for scope in self.service_original.oauth_scopes
        }
        oauth_scopes_update = {
            scope.value: scope for scope in self.service_update.oauth_scopes
        }
        for scope in set(oauth_scopes_original.keys()) - set(
            oauth_scopes_update.keys()
        ):
            self.finding_container.addFinding(
                category=FindingCategory.OAUTH_SCOPE_REMOVAL,
                proto_file_name=self.service_original.proto_file_name,
                source_code_line=oauth_scopes_original[scope].source_code_line,
                message=f"An existing oauth_scope `{scope}` is removed.",
                change_type=ChangeType.MAJOR,
            )

    def _compareRpcMethods(self):
        methods_original = self.service_original.methods
        methods_update = self.service_update.methods
        methods_original_keys = set(methods_original.keys())
        methods_update_keys = set(methods_update.keys())
        # 3.1 An RPC method is removed.
        for name in methods_original_keys - methods_update_keys:
            removed_method = methods_original[name]
            self.finding_container.addFinding(
                category=FindingCategory.METHOD_REMOVAL,
                proto_file_name=removed_method.proto_file_name,
                source_code_line=removed_method.source_code_line,
                message=f"An existing rpc method `{name}` is removed.",
                change_type=ChangeType.MAJOR,
            )
        # 3.2 An RPC method is added.
        for name in methods_update_keys - methods_original_keys:
            added_method = methods_update[name]
            self.finding_container.addFinding(
                category=FindingCategory.METHOD_ADDTION,
                proto_file_name=added_method.proto_file_name,
                source_code_line=added_method.source_code_line,
                message=f"A new rpc method `{name}` is added.",
                change_type=ChangeType.MINOR,
            )
        for name in methods_update_keys & methods_original_keys:
            method_original = methods_original[name]
            method_update = methods_update[name]
            # 3.3 The request type of an RPC method is changed.
            input_type_original = method_original.input.value
            input_type_update = method_update.input.value
            if (
                input_type_original != input_type_update
                and self._get_version_update_name(input_type_original)
                != input_type_update
            ):
                self.finding_container.addFinding(
                    category=FindingCategory.METHOD_INPUT_TYPE_CHANGE,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.input.source_code_line,
                    message=f"Input type of an existing method `{name}` is changed from `{input_type_original}` to `{input_type_update}`.",
                    change_type=ChangeType.MAJOR,
                )
            # 3.4 The response type of an RPC method is changed.
            response_type_original = method_original.output.value
            response_type_update = method_update.output.value
            if (
                response_type_original != response_type_update
                and self._get_version_update_name(response_type_original)
                != response_type_update
            ):
                self.finding_container.addFinding(
                    category=FindingCategory.METHOD_RESPONSE_TYPE_CHANGE,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.output.source_code_line,
                    message=f"Output type of an existing method `{name}` is changed from `{response_type_original}` to `{response_type_update}`.",
                    change_type=ChangeType.MAJOR,
                )
            # 3.5 The request streaming state of an RPC method is changed.
            if (
                method_original.client_streaming.value
                != method_update.client_streaming.value
            ):
                self.finding_container.addFinding(
                    category=FindingCategory.METHOD_CLIENT_STREAMING_CHANGE,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.client_streaming.source_code_line,
                    message=f"The request streaming type of an existing method `{name}` is changed.",
                    change_type=ChangeType.MAJOR,
                )
            # 3.6 The response streaming state of an RPC method is changed.
            if (
                method_original.server_streaming.value
                != method_update.server_streaming.value
            ):
                self.finding_container.addFinding(
                    category=FindingCategory.METHOD_SERVER_STREAMING_CHANGE,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.server_streaming.source_code_line,
                    message=f"The response streaming type of an existing method `{name}` is changed.",
                    change_type=ChangeType.MAJOR,
                )
            # 3.7 The paginated response of an RPC method is changed.
            if method_original.paged_result_field or method_update.paged_result_field:
                if (
                    not method_original.paged_result_field
                    or not method_update.paged_result_field
                    or method_original.paged_result_field.name
                    != method_update.paged_result_field.name
                ):
                    self.finding_container.addFinding(
                        category=FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE,
                        proto_file_name=method_update.proto_file_name,
                        source_code_line=method_update.source_code_line,
                        message=f"The paginated response of an existing method `{name}` is changed.",
                        change_type=ChangeType.MAJOR,
                    )
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
        api_version_original = self.service_original.api_version
        api_version_update = self.service_update.api_version

        if not http_annotation_original or not http_annotation_update:
            # (Aip127) APIs must provide HTTP definitions for each RPC that they define,
            # except for bi-directional streaming RPCs, so the http_annotation addition/removal indicates
            # streaming state changes of the RPC, which is a breaking change.
            if http_annotation_original and not http_annotation_update:
                self.finding_container.addFinding(
                    category=FindingCategory.HTTP_ANNOTATION_REMOVAL,
                    proto_file_name=method_original.proto_file_name,
                    source_code_line=method_original.http_annotation.source_code_line,
                    message=f"The google.api.http annotation for existing method `{method_original.name}` is removed.",
                    change_type=ChangeType.MAJOR,
                )
            if not http_annotation_original and http_annotation_update:
                self.finding_container.addFinding(
                    category=FindingCategory.HTTP_ANNOTATION_ADDITION,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.http_annotation.source_code_line,
                    message=f"A google.api.http annotation is added to method `{method_update.name}`.",
                    change_type=ChangeType.MINOR,
                )
            return
        # Compare http method, they should be identical.
        if (
            http_annotation_original["http_method"]
            != http_annotation_update["http_method"]
        ):
            self.finding_container.addFinding(
                category=FindingCategory.HTTP_ANNOTATION_CHANGE,
                proto_file_name=method_update.proto_file_name,
                source_code_line=method_update.http_annotation.source_code_line,
                message=f"An existing http method of google.api.http annotation is changed for method `{method_update.name}`.",
                change_type=ChangeType.MAJOR,
            )
        # Compare http body, they should be identical.
        if http_annotation_original["http_body"] != http_annotation_update["http_body"]:
            self.finding_container.addFinding(
                category=FindingCategory.HTTP_ANNOTATION_CHANGE,
                proto_file_name=method_update.proto_file_name,
                source_code_line=method_update.http_annotation.source_code_line,
                message=f"An existing http method body of google.api.http annotation is changed for method `{method_update.name}`.",
                change_type=ChangeType.MAJOR,
            )
        # Compare http URI, minor version updates are allowed if not identical.
        if http_annotation_original["http_uri"] != http_annotation_update["http_uri"]:
            annotation_value = http_annotation_original["http_uri"]
            transformed_value = self._get_version_update_name(annotation_value)
            if transformed_value != http_annotation_update["http_uri"]:
                self.finding_container.addFinding(
                    category=FindingCategory.HTTP_ANNOTATION_CHANGE,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.http_annotation.source_code_line,
                    message=f"An existing http method URI of google.api.http annotation is changed for method `{method_update.name}`.",
                    change_type=ChangeType.MAJOR,
                )

    def _compare_lro_annotations(self, method_original, method_update):
        lro_original = method_original.lro_annotation
        lro_update = method_update.lro_annotation
        if not lro_original and not lro_update:
            return
        # LRO operation_info annotation addition.
        if not lro_original:
            self.finding_container.addFinding(
                category=FindingCategory.LRO_ANNOTATION_ADDITION,
                proto_file_name=method_update.proto_file_name,
                source_code_line=method_update.lro_annotation.source_code_line,
                message=f"A LRO operation_info annotation is added to method `{method_update.name}`.",
                change_type=ChangeType.MINOR,
            )
            return
        # LRO operation_info annotation removal.
        if not lro_update:
            self.finding_container.addFinding(
                category=FindingCategory.LRO_ANNOTATION_REMOVAL,
                proto_file_name=method_original.proto_file_name,
                source_code_line=method_original.lro_annotation.source_code_line,
                message=f"An existing LRO operation_info annotation is removed from method `{method_update.name}`.",
                change_type=ChangeType.MINOR,
            )
            return
        # The response_type value of LRO operation_info is changed.
        if (
            lro_original.value["response_type"] != lro_update.value["response_type"]
            and self._get_version_update_name(lro_original.value["response_type"])
            != lro_update.value["response_type"]
        ):
            self.finding_container.addFinding(
                category=FindingCategory.LRO_RESPONSE_CHANGE,
                proto_file_name=method_update.proto_file_name,
                source_code_line=lro_update.source_code_line,
                message=f"The response_type of an existing LRO operation_info annotation for method `{method_update.name}` is changed from `{lro_original.value['response_type']}` to `{lro_update.value['response_type']}`.",
                change_type=ChangeType.MAJOR,
            )
        # The metadata_type value of LRO operation_info is changed.
        if (
            lro_original.value["metadata_type"] != lro_update.value["metadata_type"]
            and self._get_version_update_name(lro_original.value["metadata_type"])
            != lro_update.value["metadata_type"]
        ):
            self.finding_container.addFinding(
                category=FindingCategory.LRO_METADATA_CHANGE,
                proto_file_name=method_update.proto_file_name,
                source_code_line=lro_update.source_code_line,
                message=f"The metadata_type of an existing LRO operation_info annotation for method `{method_update.name}` is changed from `{lro_original.value['metadata_type']}` to `{lro_update.value['metadata_type']}`.",
                change_type=ChangeType.MAJOR,
            )

    def _compare_method_signatures(self, method_original, method_update):
        signatures_original = method_original.method_signatures.value
        signatures_update = method_update.method_signatures.value
        if len(signatures_original) > len(signatures_update):
            self.finding_container.addFinding(
                category=FindingCategory.METHOD_SIGNATURE_CHANGE,
                proto_file_name=method_original.proto_file_name,
                source_code_line=method_original.method_signatures.source_code_line,
                message=f"An existing method_signature is removed from method `{method_original.name}`.",
                change_type=ChangeType.MAJOR,
            )
        for old_sig, new_sig in zip(signatures_original, signatures_update):
            if old_sig != new_sig:
                self.finding_container.addFinding(
                    category=FindingCategory.METHOD_SIGNATURE_CHANGE,
                    proto_file_name=method_update.proto_file_name,
                    source_code_line=method_update.method_signatures.source_code_line,
                    message=f"An existing method_signature for method `{method_update.name}` is changed from `{old_sig}` to `{new_sig}`.",
                    change_type=ChangeType.MAJOR,
                )

    def _get_version_update_name(self, name):
        original_version = self.service_original.api_version
        update_version = self.service_update.api_version
        if not original_version or not update_version:
            return name
        return name.replace(original_version, update_version)

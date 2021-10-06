import unittest
from src.comparator.service_comparator import ServiceComparator
from test.tools.mock_descriptors import (
    make_service,
    make_method,
    make_message,
    make_field,
)
from src.findings.finding_container import FindingContainer


class ServiceComparatorTest(unittest.TestCase):
    def setUp(self):
        self.service_foo = make_service(name="Foo")
        self.finding_container = FindingContainer()

    def test_service_removal(self):
        ServiceComparator(
            self.service_foo, None, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "SERVICE_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_service_addition(self):
        ServiceComparator(
            None, self.service_foo, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "SERVICE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_service_host_addition(self):
        service_without_host = make_service()
        service_with_host = make_service(host="api.google.com")
        ServiceComparator(
            service_without_host,
            service_with_host,
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "SERVICE_HOST_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_service_host_removal(self):
        service_without_host = make_service()
        service_with_host = make_service(host="api.google.com")
        ServiceComparator(
            service_with_host,
            service_without_host,
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "SERVICE_HOST_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_service_host_change(self):
        service_original = make_service(host="default.host")
        service_update = make_service(host="default.host.update")
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "SERVICE_HOST_CHANGE")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_service_oauth_scopes_change(self):
        service_original = make_service(
            scopes=("https://foo/user/", "https://foo/admin/")
        )
        service_update = make_service(
            scopes=("https://www.googleapis.com/auth/cloud-platform")
        )
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "OAUTH_SCOPE_REMOVAL"
            and f.subject == "https://foo/user/"
        )
        self.assertEqual(finding.location.proto_file_name, "foo")
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "OAUTH_SCOPE_REMOVAL"
            and f.subject == "https://foo/admin/"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_removal(self):
        method_foo = make_method(name="foo")
        method_bar = make_method(name="bar")
        service_original = make_service(methods=(method_foo, method_bar))
        service_update = make_service(methods=(method_foo,))
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "METHOD_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_addition(self):
        method_foo = make_method(name="foo")
        method_bar = make_method(name="bar")
        service_original = make_service(methods=(method_foo,))
        service_update = make_service(methods=(method_foo, method_bar))
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "METHOD_ADDTION")
        self.assertEqual(finding.change_type.name, "MINOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_input_type_change(self):
        message_foo_request = make_message(name="FooRequest", full_name="FooRequest")
        message_bar_request = make_message(name="BarRequest", full_name="BarRequest")
        service_original = make_service(
            methods=(make_method(name="Foo", input_message=message_foo_request),)
        )
        service_update = make_service(
            methods=(make_method(name="Foo", input_message=message_bar_request),)
        )
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "METHOD_INPUT_TYPE_CHANGE"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_output_type_change(self):
        service_original = make_service(
            methods=(
                make_method(
                    name="Foo",
                    output_message=make_message(
                        name="FooResponse", full_name=".example.FooResponse"
                    ),
                ),
            )
        )
        service_update = make_service(
            methods=(
                make_method(
                    name="Foo",
                    output_message=make_message(
                        name="BarResponse", full_name=".example.BarResponse"
                    ),
                ),
            )
        )
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "METHOD_RESPONSE_TYPE_CHANGE"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_streaming_state_change(self):
        service_original = make_service(
            methods=(make_method(name="Bar", client_streaming=True),)
        )
        service_update = make_service(
            methods=(make_method(name="Bar", server_streaming=True),)
        )
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()

        client_streaming_finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "METHOD_CLIENT_STREAMING_CHANGE"
        )
        self.assertEqual(client_streaming_finding.location.proto_file_name, "foo")
        server_streaming_finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "METHOD_SERVER_STREAMING_CHANGE"
        )
        self.assertEqual(server_streaming_finding.change_type.name, "MAJOR")
        self.assertEqual(server_streaming_finding.location.proto_file_name, "foo")

    def test_method_paginated_state_change(self):
        paginated_response_message = make_message(
            name="PaginatedResponseMessage",
            fields=[
                make_field(
                    name="repeated_field",
                    proto_type="TYPE_STRING",
                    repeated=True,
                    number=1,
                ),
                make_field(
                    name="next_page_token",
                    proto_type="TYPE_STRING",
                    number=2,
                ),
            ],
            full_name=".example.v1.PaginatedResponseMessage",
        )
        paginated_request_message = make_message(
            name="PaginatedRequestMessage",
            fields=[
                make_field(
                    name="page_size",
                    proto_type="TYPE_INT32",
                    number=1,
                ),
                make_field(
                    name="page_token",
                    proto_type="TYPE_STRING",
                    number=2,
                ),
            ],
            full_name=".example.v1.PaginatedRequestMessage",
        )
        messages_map_original = {
            ".example.v1.PaginatedResponseMessage": paginated_response_message,
            ".example.v1.PaginatedRequestMessage": paginated_request_message,
        }
        paged_method = make_method(
            name="notInteresting",
            input_message=paginated_request_message,
            output_message=paginated_response_message,
        )
        messages_map_update = {
            ".example.v1alpha.MethodInput": make_message(
                name="MethodInput", full_name=".example.v1alpha.MethodInput"
            ),
            ".example.v1alpha.MethodOutput": make_message(
                name="MethodOutput", full_name=".example.v1alpha.MethodOutput"
            ),
        }
        non_paged_method = make_method(name="notInteresting")
        service_original = make_service(
            methods=(paged_method,), messages_map=messages_map_original
        )
        service_update = make_service(
            methods=(non_paged_method,), messages_map=messages_map_update
        )
        ServiceComparator(
            service_original, service_update, self.finding_container, context="ctx"
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "METHOD_PAGINATED_RESPONSE_CHANGE"
        )
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_signature_removal(self):
        ServiceComparator(
            make_service(
                methods=(
                    make_method(name="notInteresting", signatures=["sig1", "sig2"]),
                )
            ),
            make_service(
                methods=(make_method(name="notInteresting", signatures=["sig1"]),)
            ),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "METHOD_SIGNATURE_REMOVAL"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_lro_annotation_addition(self):
        lro_output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method_lro = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type",
            lro_metadata_type="FooMetadata",
        )
        method_not_lro = make_method(
            name="Method",
        )
        ServiceComparator(
            make_service(methods=(method_not_lro,)),
            make_service(methods=(method_lro,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "LRO_ANNOTATION_ADDITION"
        )
        self.assertTrue(finding)

    def test_lro_annotation_removal(self):
        lro_output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method_lro = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type",
            lro_metadata_type="FooMetadata",
        )
        method_not_lro = make_method(
            name="Method",
        )
        ServiceComparator(
            make_service(methods=(method_lro,)),
            make_service(methods=(method_not_lro,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "LRO_ANNOTATION_REMOVAL"
        )
        self.assertTrue(finding)

    def test_lro_annotation_invalid(self):
        lro_output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method_lro = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type",
            lro_metadata_type="FooMetadata",
        )
        method_not_lro = make_method(
            name="Method",
            output_message=lro_output_msg,
        )
        # `method_not_lro` returns `google.longrunning.Operation`
        # but is missing a response type or metadata type, the definition
        # is invalid. We still compare the two methods and take it as
        # lro annotation removal.
        ServiceComparator(
            make_service(methods=(method_lro,)),
            make_service(methods=(method_not_lro,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "LRO_ANNOTATION_REMOVAL"
        )
        self.assertTrue(finding)

    def test_lro_annotation_response_change(self):
        lro_output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method_original = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type",
            lro_metadata_type="FooMetadata",
        )
        method_update = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type_update",
            lro_metadata_type="FooMetadata",
        )
        ServiceComparator(
            make_service(methods=(method_original,)),
            make_service(methods=(method_update,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "LRO_RESPONSE_CHANGE"
        )
        self.assertEqual(finding.change_type.name, "MAJOR")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_lro_annotation_metadata_change(self):
        lro_output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method_original = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type",
            lro_metadata_type="FooMetadata",
        )
        method_update = make_method(
            name="Method",
            output_message=lro_output_msg,
            lro_response_type="response_type",
            lro_metadata_type="FooMetadataUpdate",
        )
        ServiceComparator(
            make_service(methods=(method_original,)),
            make_service(methods=(method_update,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "LRO_METADATA_CHANGE"
        )
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_http_annotation_addition(self):
        method_without_http_annotation = make_method(
            name="Method",
        )
        method_with_http_annotation = make_method(
            name="Method",
            http_uri="http_uri_update",
            http_body="http_body",
        )
        ServiceComparator(
            make_service(methods=(method_without_http_annotation,)),
            make_service(methods=(method_with_http_annotation,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "HTTP_ANNOTATION_ADDITION")
        self.assertEqual(finding.change_type.name, "MINOR")

    def test_http_annotation_removal(self):
        method_without_http_annotation = make_method(
            name="Method",
        )
        method_with_http_annotation = make_method(
            name="Method",
            http_uri="http_uri_update",
            http_body="http_body",
        )
        ServiceComparator(
            make_service(methods=(method_with_http_annotation,)),
            make_service(methods=(method_without_http_annotation,)),
            self.finding_container,
            context="ctx",
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.category.name, "HTTP_ANNOTATION_REMOVAL")
        self.assertEqual(finding.change_type.name, "MAJOR")

    def test_http_annotation_change(self):
        method_original = make_method(
            name="Method",
            http_uri="http_uri",
            http_body="*",
        )
        method_update = make_method(
            name="Method",
            http_uri="http_uri_update",
            http_body="http_body",
        )
        ServiceComparator(
            make_service(methods=(method_original,)),
            make_service(methods=(method_update,)),
            self.finding_container,
            context="ctx",
        ).compare()
        uri_change_finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "HTTP_ANNOTATION_CHANGE" and f.type == "http_uri"
        )
        body_change_finding = next(
            f
            for f in self.finding_container.getAllFindings()
            if f.category.name == "HTTP_ANNOTATION_CHANGE" and f.type == "http_body"
        )
        self.assertEqual(
            uri_change_finding.location.proto_file_name,
            "foo",
        )
        self.assertEqual(
            body_change_finding.location.proto_file_name,
            "foo",
        )

    def test_http_annotation_minor_version_update(self):
        method_original = make_method(
            name="Method",
            http_uri="/v1/{name=projects/*}",
            http_body="*",
        )
        method_update = make_method(
            name="Method",
            http_uri="/v1alpha/{name=projects/*}",
            http_body="*",
        )
        ServiceComparator(
            make_service(methods=(method_original,), api_version="v1"),
            make_service(methods=(method_update,), api_version="v1alpha"),
            self.finding_container,
            context="ctx",
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        # No breaking changes, since only minor version update in the http URI.
        self.assertFalse(findings_map)


if __name__ == "__main__":
    unittest.main()

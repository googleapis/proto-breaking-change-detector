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
        ServiceComparator(self.service_foo, None, self.finding_container).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "An existing service `Foo` is removed.")
        self.assertEqual(finding.category.name, "SERVICE_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_service_addition(self):
        ServiceComparator(
            None,
            self.service_foo,
            self.finding_container,
        ).compare()
        finding = self.finding_container.getAllFindings()[0]
        self.assertEqual(finding.message, "A new service `Foo` is added.")
        self.assertEqual(finding.category.name, "SERVICE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_removal(self):
        method_foo = make_method(name="foo")
        method_bar = make_method(name="bar")
        service_original = make_service(methods=(method_foo, method_bar))
        service_update = make_service(methods=(method_foo,))
        ServiceComparator(
            service_original, service_update, self.finding_container
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map["An existing rpc method `bar` is removed."]
        self.assertEqual(finding.category.name, "METHOD_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_input_type_change(self):
        message_foo_request = make_message(name="FooRequest")
        message_bar_request = make_message(name="BarRequest")
        service_original = make_service(
            methods=(make_method(name="Foo", input_message=message_foo_request),)
        )
        service_update = make_service(
            methods=(make_method(name="Foo", input_message=message_bar_request),)
        )
        ServiceComparator(
            service_original, service_update, self.finding_container
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map[
            "Input type of an existing method `Foo` is changed from `FooRequest` to `BarRequest`."
        ]
        self.assertEqual(finding.category.name, "METHOD_INPUT_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_output_type_change(self):
        service_original = make_service(
            methods=(
                make_method(
                    name="Foo", output_message=make_message(name="FooResponse")
                ),
            )
        )
        service_update = make_service(
            methods=(
                make_method(
                    name="Foo", output_message=make_message(name="BarResponse")
                ),
            )
        )
        ServiceComparator(
            service_original, service_update, self.finding_container
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map[
            "Output type of an existing method `Foo` is changed from `FooResponse` to `BarResponse`."
        ]
        self.assertEqual(finding.category.name, "METHOD_RESPONSE_TYPE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_streaming_state_change(self):
        service_original = make_service(
            methods=(make_method(name="Bar", client_streaming=True),)
        )
        service_update = make_service(
            methods=(make_method(name="Bar", server_streaming=True),)
        )
        ServiceComparator(
            service_original, service_update, self.finding_container
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        client_streaming_finding = findings_map[
            "The request streaming type of an existing method `Bar` is changed."
        ]
        self.assertEqual(
            client_streaming_finding.category.name, "METHOD_CLIENT_STREAMING_CHANGE"
        )
        self.assertEqual(client_streaming_finding.location.proto_file_name, "foo")
        server_streaming_finding = findings_map[
            "The response streaming type of an existing method `Bar` is changed."
        ]
        self.assertEqual(
            server_streaming_finding.category.name, "METHOD_SERVER_STREAMING_CHANGE"
        )
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
        )
        messages_map_original = {
            "PaginatedResponseMessage": paginated_response_message,
            "PaginatedRequestMessage": paginated_request_message,
        }
        paged_method = make_method(
            name="notInteresting",
            input_message=paginated_request_message,
            output_message=paginated_response_message,
        )
        messages_map_update = {
            "MethodInput": make_message(name="MethodInput"),
            "MethodOutput": make_message(name="MethodOutput"),
        }
        non_paged_method = make_method(name="notInteresting")
        service_original = make_service(
            methods=(paged_method,), messages_map=messages_map_original
        )
        service_update = make_service(
            methods=(non_paged_method,), messages_map=messages_map_update
        )
        ServiceComparator(
            service_original, service_update, self.finding_container
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map[
            "The paginated response of an existing method `notInteresting` is changed."
        ]
        self.assertEqual(finding.category.name, "METHOD_PAGINATED_RESPONSE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_method_signature_change(self):
        ServiceComparator(
            make_service(
                methods=(
                    make_method(name="notInteresting", signatures=["sig1", "sig2"]),
                )
            ),
            make_service(
                methods=(
                    make_method(name="notInteresting", signatures=["sig2", "sig1"]),
                )
            ),
            self.finding_container,
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map[
            "An existing method_signature for method `notInteresting` is changed from `sig1` to `sig2`."
        ]
        self.assertEqual(finding.category.name, "METHOD_SIGNATURE_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

    def test_lro_annotation_change(self):
        lro_output_msg = make_message(name=".google.longrunning.Operation")
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
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        finding = findings_map[
            "The metadata_type of an existing LRO operation_info annotation for method `Method` is changed from `FooMetadata` to `FooMetadataUpdate`."
        ]
        self.assertEqual(finding.category.name, "LRO_METADATA_CHANGE")
        self.assertEqual(finding.location.proto_file_name, "foo")

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
        ).compare()
        findings_map = {f.message: f for f in self.finding_container.getAllFindings()}
        # TODO(xiaozhenliu): This should be removed once we have version updates
        # support. The URI update from `v1/example:foo` to `v1beta1/example:foo`
        # is allowed.
        uri_change_finding = findings_map[
            "An existing http method URI of google.api.http annotation is changed for method `Method`."
        ]
        body_change_finding = findings_map[
            "An existing http method body of google.api.http annotation is changed for method `Method`."
        ]

        self.assertEqual(uri_change_finding.category.name, "HTTP_ANNOTATION_CHANGE")
        self.assertEqual(
            uri_change_finding.location.proto_file_name,
            "foo",
        )
        self.assertEqual(body_change_finding.category.name, "HTTP_ANNOTATION_CHANGE")
        self.assertEqual(
            body_change_finding.location.proto_file_name,
            "foo",
        )


if __name__ == "__main__":
    unittest.main()

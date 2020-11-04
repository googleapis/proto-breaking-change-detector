import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.service_comparator import ServiceComparator
from src.comparator.wrappers import FileSet
from src.findings.finding_container import FindingContainer


class DescriptorComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.service_comparator.ServiceComparator class.
    # We use service_v1.proto and service_v1beta1.proto to mimic the original and next
    # versions of the API definition files (which has only one proto file in this case).
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.
    _INVOKER_SERVICE_ORIGNAL = UnittestInvoker(
        ["service_v1.proto"], "service_v1_descriptor_set.pb"
    )
    _INVOKER_SERVICE_UPDATE = UnittestInvoker(
        ["service_v1beta1.proto"], "service_v1beta1_descriptor_set.pb"
    )
    _INVOKER_ANNOTATION_ORIGNAL = UnittestInvoker(
        ["service_annotation_v1.proto"], "service_annotation_v1_descriptor_set.pb", True
    )
    _INVOKER_ANNOTATION_UPDATE = UnittestInvoker(
        ["service_annotation_v1beta1.proto"],
        "service_annotation_v1beta1_descriptor_set.pb",
        True,
    )

    def setUp(self):
        # Get `Example` service from the original and updated `service_*.proto` files.
        self.service_original = FileSet(
            self._INVOKER_SERVICE_ORIGNAL.run()
        ).services_map["Example"]
        self.service_update = FileSet(self._INVOKER_SERVICE_UPDATE.run()).services_map[
            "Example"
        ]
        # Get `Example` service from the original and updated `service_annotation_*.proto` files.
        self.service_annotation_original = FileSet(
            self._INVOKER_ANNOTATION_ORIGNAL.run()
        ).services_map["Example"]
        self.service_annotation_update = FileSet(
            self._INVOKER_ANNOTATION_UPDATE.run()
        ).services_map["Example"]

    def tearDown(self):
        FindingContainer.reset()

    def test_service_removal(self):
        ServiceComparator(
            self.service_original,
            None,
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A service Example is removed")
        self.assertEqual(finding.category.name, "SERVICE_REMOVAL")
        self.assertEqual(finding.location.proto_file_name, "service_v1.proto")
        self.assertEqual(finding.location.source_code_line, 5)

    def test_service_addition(self):
        ServiceComparator(
            None,
            self.service_original,
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new service Example is added.")
        self.assertEqual(finding.category.name, "SERVICE_ADDITION")
        self.assertEqual(finding.location.proto_file_name, "service_v1.proto")
        self.assertEqual(finding.location.source_code_line, 5)

    def test_method_change(self):
        ServiceComparator(
            self.service_original,
            self.service_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        # Method removal.
        method_removal_finding = findings_map["An rpc method shouldRemove is removed"]
        self.assertEqual(method_removal_finding.category.name, "METHOD_REMOVAL")
        self.assertEqual(
            method_removal_finding.location.proto_file_name, "service_v1.proto"
        )
        self.assertEqual(method_removal_finding.location.source_code_line, 11)
        # Input type change.
        method_input_change = findings_map[
            "Input type of method Foo is changed from FooRequest to FooRequestUpdate"
        ]
        self.assertEqual(method_input_change.category.name, "METHOD_INPUT_TYPE_CHANGE")
        self.assertEqual(
            method_input_change.location.proto_file_name, "service_v1beta1.proto"
        )
        self.assertEqual(method_input_change.location.source_code_line, 7)
        # Output type change.
        method_output_change = findings_map[
            "Output type of method Foo is changed from FooResponse to FooResponseUpdate"
        ]
        self.assertEqual(
            method_output_change.category.name, "METHOD_RESPONSE_TYPE_CHANGE"
        )
        self.assertEqual(
            method_output_change.location.proto_file_name, "service_v1beta1.proto"
        )
        self.assertEqual(method_output_change.location.source_code_line, 7)
        # Streaming state change.
        method_client_streaming_change = findings_map[
            "The request streaming type of method Bar is changed"
        ]
        self.assertEqual(
            method_client_streaming_change.category.name,
            "METHOD_CLIENT_STREAMING_CHANGE",
        )
        self.assertEqual(
            method_client_streaming_change.location.proto_file_name,
            "service_v1beta1.proto",
        )
        self.assertEqual(method_client_streaming_change.location.source_code_line, 9)
        method_server_streaming_change = findings_map[
            "The response streaming type of method Bar is changed"
        ]
        self.assertEqual(
            method_server_streaming_change.category.name,
            "METHOD_SERVER_STREAMING_CHANGE",
        )
        self.assertEqual(
            method_server_streaming_change.location.proto_file_name,
            "service_v1beta1.proto",
        )
        self.assertEqual(method_server_streaming_change.location.source_code_line, 9)
        # Paginated state change.
        paginated_change = findings_map[
            "The paginated response of method paginatedMethod is changed"
        ]
        self.assertEqual(
            paginated_change.category.name, "METHOD_PAGINATED_RESPONSE_CHANGE"
        )
        self.assertEqual(
            paginated_change.location.proto_file_name, "service_v1beta1.proto"
        )
        self.assertEqual(paginated_change.location.source_code_line, 11)

    def test_method_signature_change(self):
        ServiceComparator(
            self.service_annotation_original,
            self.service_annotation_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "An existing method_signature is changed from 'content' to 'error'."
        ]
        self.assertEqual(finding.category.name, "METHOD_SIGNATURE_CHANGE")
        self.assertEqual(
            finding.location.proto_file_name, "service_annotation_v1beta1.proto"
        )
        self.assertEqual(finding.location.source_code_line, 18)

    def test_lro_annotation_change(self):
        ServiceComparator(
            self.service_annotation_original,
            self.service_annotation_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        finding = findings_map[
            "The metadata_type of LRO operation_info annotation is changed from FooMetadata to FooMetadataUpdate"
        ]
        self.assertEqual(finding.category.name, "LRO_METADATA_CHANGE")
        self.assertEqual(
            finding.location.proto_file_name, "service_annotation_v1beta1.proto"
        )
        self.assertEqual(finding.location.source_code_line, 26)

    def test_http_annotation_change(self):
        ServiceComparator(
            self.service_annotation_original,
            self.service_annotation_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        # TODO(xiaozhenliu): This should be removed once we have version updates
        # support. The URI update from `v1/example:foo` to `v1beta1/example:foo`
        # is allowed.
        uri_change_finding = findings_map["An existing http method URI is changed."]
        method_change_finding = findings_map["An existing http method is changed."]
        body_change_finding = findings_map["An existing http method body is changed."]

        self.assertEqual(uri_change_finding.category.name, "HTTP_ANNOTATION_CHANGE")
        self.assertEqual(
            uri_change_finding.location.proto_file_name,
            "service_annotation_v1beta1.proto",
        )
        self.assertEqual(uri_change_finding.location.source_code_line, 14)
        self.assertEqual(method_change_finding.category.name, "HTTP_ANNOTATION_CHANGE")
        self.assertEqual(
            method_change_finding.location.proto_file_name,
            "service_annotation_v1beta1.proto",
        )
        self.assertEqual(method_change_finding.location.source_code_line, 14)
        self.assertEqual(body_change_finding.category.name, "HTTP_ANNOTATION_CHANGE")
        self.assertEqual(
            body_change_finding.location.proto_file_name,
            "service_annotation_v1beta1.proto",
        )
        self.assertEqual(body_change_finding.location.source_code_line, 22)

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_SERVICE_ORIGNAL.cleanup()
        cls._INVOKER_SERVICE_UPDATE.cleanup()
        cls._INVOKER_ANNOTATION_ORIGNAL.cleanup()
        cls._INVOKER_ANNOTATION_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

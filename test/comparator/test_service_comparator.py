import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.service_comparator import ServiceComparator
from src.comparator.wrappers import Service
from src.comparator.wrappers import Message
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
        service_v1_pb = self._INVOKER_SERVICE_ORIGNAL.run()
        service_v1beta1_pb = self._INVOKER_SERVICE_UPDATE.run()
        self.messages_map_original = {
            m.name: Message(m) for m in service_v1_pb.file[0].message_type
        }
        self.messages_map_update = {
            m.name: Message(m) for m in service_v1beta1_pb.file[0].message_type
        }
        self.service_original = Service(
            service_v1_pb.file[0].service[0], self.messages_map_original
        )
        self.service_update = Service(
            service_v1beta1_pb.file[0].service[0], self.messages_map_update
        )
        # Get `Example` service from the original and updated `service_annotation_*.proto` files.
        service_annotation_v1_pb = self._INVOKER_ANNOTATION_ORIGNAL.run()
        service_annotation_v1beta1_pb = self._INVOKER_ANNOTATION_UPDATE.run()
        self.annotation_messages_map_original = {
            m.name: Message(m) for m in service_annotation_v1_pb.file[0].message_type
        }
        self.annotation_messages_map_update = {
            m.name: Message(m)
            for m in service_annotation_v1beta1_pb.file[0].message_type
        }
        self.service_annotation_original = Service(
            service_annotation_v1_pb.file[0].service[0],
            self.annotation_messages_map_original,
        )
        self.service_annotation_update = Service(
            service_annotation_v1beta1_pb.file[0].service[0],
            self.annotation_messages_map_update,
        )

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

    def test_service_addition(self):
        ServiceComparator(
            None,
            self.service_original,
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new service Example is added.")
        self.assertEqual(finding.category.name, "SERVICE_ADDITION")

    def test_method_change(self):
        ServiceComparator(
            self.service_original,
            self.service_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map["An rpc method shouldRemove is removed"].category.name,
            "METHOD_REMOVAL",
        )
        self.assertEqual(
            findings_map[
                "Input type of method Foo is changed from FooRequest to FooRequestUpdate"
            ].category.name,
            "METHOD_INPUT_TYPE_CHANGE",
        )
        self.assertEqual(
            findings_map[
                "Output type of method Foo is changed from FooResponse to FooResponseUpdate"
            ].category.name,
            "METHOD_RESPONSE_TYPE_CHANGE",
        )
        self.assertEqual(
            findings_map[
                "The request streaming type of method Bar is changed"
            ].category.name,
            "METHOD_CLIENT_STREAMING_CHANGE",
        )
        self.assertEqual(
            findings_map[
                "The response streaming type of method Bar is changed"
            ].category.name,
            "METHOD_SERVER_STREAMING_CHANGE",
        )
        self.assertEqual(
            findings_map[
                "The paginated response of method paginatedMethod is changed"
            ].category.name,
            "METHOD_PAGINATED_RESPONSE_CHANGE",
        )

    def test_method_signature_change(self):
        ServiceComparator(
            self.service_annotation_original,
            self.service_annotation_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map.get(
                "An existing method_signature is changed from 'content' to 'error'."
            ).category.name,
            "METHOD_SIGNATURE_CHANGE",
        )

    def test_lro_annotation_change(self):
        ServiceComparator(
            self.service_annotation_original,
            self.service_annotation_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map.get(
                "The metadata_type of LRO operation_info annotation is changed from FooMetadata to FooMetadataUpdate"
            ).category.name,
            "LRO_METADATA_CHANGE",
        )

    def test_http_annotation_change(self):
        ServiceComparator(
            self.service_annotation_original,
            self.service_annotation_update,
        ).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        # TODO(xiaozhenliu): This should be removed once we have version updates
        # support. The URI update from `v1/example:foo` to `v1beta1/example:foo`
        # is allowed.
        self.assertEqual(
            findings_map.get("An existing http method URI is changed.").category.name,
            "HTTP_ANNOTATION_CHANGE",
        )
        self.assertEqual(
            findings_map.get("An existing http method is changed.").category.name,
            "HTTP_ANNOTATION_CHANGE",
        )
        self.assertEqual(
            findings_map.get("An existing http method body is changed.").category.name,
            "HTTP_ANNOTATION_CHANGE",
        )

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_SERVICE_ORIGNAL.cleanup()
        cls._INVOKER_SERVICE_UPDATE.cleanup()
        cls._INVOKER_ANNOTATION_ORIGNAL.cleanup()
        cls._INVOKER_ANNOTATION_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

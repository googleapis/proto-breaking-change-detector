import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.service_comparator import ServiceComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class DescriptorComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.service_comparator.ServiceComparator class.
    # We use service_v1.proto and service_v1beta1.proto to mimic the original and next
    # versions of the API definition files (which has only one proto file in this case).
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.
    _PROTO_ORIGINAL = "service_v1.proto"
    _PROTO_UPDATE = "service_v1beta1.proto"
    _DESCRIPTOR_SET_ORIGINAL = "service_v1_descriptor_set.pb"
    _DESCRIPTOR_SET_UPDATE = "service_v1beta1_descriptor_set.pb"
    _INVOKER_ORIGNAL = UnittestInvoker([_PROTO_ORIGINAL], _DESCRIPTOR_SET_ORIGINAL)
    _INVOKER_UPDATE = UnittestInvoker([_PROTO_UPDATE], _DESCRIPTOR_SET_UPDATE)
    _PB_ORIGNAL = _INVOKER_ORIGNAL.run()
    _PB_UPDATE = _INVOKER_UPDATE.run()

    def setUp(self):
        # Get `Example` service from the original and updated `*_descriptor_set.pb` files.
        self.service_original = self._PB_ORIGNAL.file[0].service[0]
        self.service_update = self._PB_UPDATE.file[0].service[0]
        self.messages_map_original = {
            m.name: m for m in self._PB_ORIGNAL.file[0].message_type
        }
        self.messages_map_update = {
            m.name: m for m in self._PB_UPDATE.file[0].message_type
        }

    def tearDown(self):
        FindingContainer.reset()

    def test_service_removal(self):
        ServiceComparator(
            self.service_original,
            None,
            self.messages_map_original,
            self.messages_map_update,
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A service Example is removed")
        self.assertEqual(finding.category.name, "SERVICE_REMOVAL")

    def test_service_addition(self):
        ServiceComparator(
            None,
            self.service_original,
            self.messages_map_original,
            self.messages_map_update,
        ).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, "A new service Example is added.")
        self.assertEqual(finding.category.name, "SERVICE_ADDITION")

    def test_method_change(self):
        ServiceComparator(
            self.service_original,
            self.service_update,
            self.messages_map_original,
            self.messages_map_update,
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

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.file_set_comparator import FileSetComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class FileSetComparatorTest(unittest.TestCase):
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

    def tearDown(self):
        FindingContainer.reset()

    def test_service_change(self):
        FileSetComparator(self._PB_ORIGNAL, self._PB_UPDATE).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map[
                "The paginated response of method paginatedMethod is changed"
            ].category.name,
            "METHOD_PAGINATED_RESPONSE_CHANGE",
        )

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

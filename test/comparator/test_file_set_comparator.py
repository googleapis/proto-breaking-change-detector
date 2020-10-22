import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.file_set_comparator import FileSetComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class FileSetComparatorTest(unittest.TestCase):
    # This is for tesing the behavior of src.comparator.service_comparator.ServiceComparator class.
    # UnittestInvoker helps us to execute the protoc command to compile the proto file,
    # get a *_descriptor_set.pb file (by -o option) which contains the serialized data in protos, and
    # create a FileDescriptorSet (_PB_ORIGNAL and _PB_UPDATE) out of it.

    def tearDown(self):
        FindingContainer.reset()

    def test_service_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["service_v1.proto"], "service_v1_descriptor_set.pb"
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["service_v1beta1.proto"], "service_v1beta1_descriptor_set.pb"
        )
        FileSetComparator(_INVOKER_ORIGNAL.run(), _INVOKER_UPDATE.run()).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map[
                "The paginated response of method paginatedMethod is changed"
            ].category.name,
            "METHOD_PAGINATED_RESPONSE_CHANGE",
        )
        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()

    def test_message_change(self):
        _INVOKER_ORIGNAL = UnittestInvoker(
            ["message_v1.proto"], "message_v1_descriptor_set.pb"
        )
        _INVOKER_UPDATE = UnittestInvoker(
            ["message_v1beta1.proto"], "message_v1beta1_descriptor_set.pb"
        )
        FileSetComparator(_INVOKER_ORIGNAL.run(), _INVOKER_UPDATE.run()).compare()
        findings_map = {f.message: f for f in FindingContainer.getAllFindings()}
        self.assertEqual(
            findings_map[
                "Type of the field is changed, the original is TYPE_INT32, but the updated is TYPE_STRING"
            ].category.name,
            "FIELD_TYPE_CHANGE",
        )
        _INVOKER_ORIGNAL.cleanup()
        _INVOKER_UPDATE.cleanup()


if __name__ == "__main__":
    unittest.main()

import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.message_comparator import DescriptorComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory

class DescriptorComparatorTest(unittest.TestCase):
    _PROTO_ORIGINAL = 'address_book.proto'
    _PROTO_UPDATE = 'address_book_update.proto'
    _DESCRIPTOR_SET_ORIGINAL = 'address_book_descriptor_set.pb'
    _DESCRIPTOR_SET_UPDATE = 'address_book_descriptor_set_update.pb'
    _INVOKER_ORIGNAL = UnittestInvoker([_PROTO_ORIGINAL], _DESCRIPTOR_SET_ORIGINAL)
    _INVOKER_UPDATE = UnittestInvoker([_PROTO_UPDATE], _DESCRIPTOR_SET_UPDATE)
    _PB_ORIGNAL = _INVOKER_ORIGNAL.run()
    _PB_UPDATE = _INVOKER_UPDATE.run()

    def setUp(self):
        self.person_msg = self._PB_ORIGNAL.file[0].message_type[0]
        self.person_msg_update = self._PB_UPDATE.file[0].message_type[0]
        self.addressBook_msg = self._PB_ORIGNAL.file[0].message_type[1]
        self.addressBook_msg_update = self._PB_UPDATE.file[0].message_type[1]

    def tearDown(self):
        FindingContainer.reset()

    def test_message_removal(self):
        DescriptorComparator(self.person_msg, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A message Person is removed')
        self.assertEqual(finding.category.name, 'MESSAGE_REMOVAL')

    def test_message_addition(self):
        DescriptorComparator(None, self.addressBook_msg).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A new message AddressBook is added.')
        self.assertEqual(finding.category.name, 'MESSAGE_ADDITION')  

    def test_field_change(self):
        DescriptorComparator(self.person_msg, self.person_msg_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'Type of the field is changed, the original is TYPE_INT32, but the updated is TYPE_STRING')
        self.assertEqual(finding.category.name, 'FIELD_TYPE_CHANGE')  

    def test_nested_message_change(self):
        # Field `type` in nested message `PhoneNumber` is removed.
        DescriptorComparator(self.person_msg, self.person_msg_update).compare()
        findingLength = len(FindingContainer.getAllFindings())
        self.assertEqual(FindingContainer.getAllFindings()[findingLength - 1].category.name, 'FIELD_REMOVAL')
    
    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()

if __name__ == '__main__':
    unittest.main()

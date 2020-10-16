import unittest
from test.tools.invoker import UnittestInvoker
from src.comparator.enum_comparator import EnumComparator
from src.findings.finding_container import FindingContainer


class EnumComparatorTest(unittest.TestCase):
    _PROTO_ORIGINAL = 'address_book.proto'
    _PROTO_UPDATE = 'address_book_update.proto'
    _DESCRIPTOR_SET_ORIGINAL = 'address_book_descriptor_set.pb'
    _DESCRIPTOR_SET_UPDATE = 'address_book_descriptor_set_update.pb'
    _INVOKER_ORIGNAL = UnittestInvoker(
        [_PROTO_ORIGINAL], _DESCRIPTOR_SET_ORIGINAL)
    _INVOKER_UPDATE = UnittestInvoker([_PROTO_UPDATE], _DESCRIPTOR_SET_UPDATE)
    _PB_ORIGNAL = _INVOKER_ORIGNAL.run()
    _PB_UPDATE = _INVOKER_UPDATE.run()

    def setUp(self):
        self.enum_original = \
            self._PB_ORIGNAL.file[0].message_type[0].enum_type[0]
        self.enum_update = self._PB_UPDATE.file[0].message_type[0].enum_type[0]

    def tearDown(self):
        FindingContainer.reset()

    def test_enum_removal(self):
        EnumComparator(self.enum_original, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'An Enum PhoneType is removed')
        self.assertEqual(finding.category.name, 'ENUM_REMOVAL')

    def test_enum_addition(self):
        EnumComparator(None, self.enum_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A new Enum PhoneType is added.')
        self.assertEqual(finding.category.name, 'ENUM_ADDITION')

    def test_enum_value_change(self):
        EnumComparator(self.enum_original, self.enum_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A new EnumValue SCHOOL is added.')
        self.assertEqual(finding.category.name, 'ENUM_VALUE_ADDITION')

    def test_no_api_change(self):
        EnumComparator(self.enum_update, self.enum_update).compare()
        self.assertEqual(len(FindingContainer.getAllFindings()), 0)

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER_ORIGNAL.cleanup()
        cls._INVOKER_UPDATE.cleanup()


if __name__ == '__main__':
    unittest.main()

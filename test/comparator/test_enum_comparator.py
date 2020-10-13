import unittest
import test.testdata.original_pb2 as original_version
import test.testdata.update_pb2 as update_version
from src.comparator.enum_comparator import EnumComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory

class EnumComparatorTest(unittest.TestCase):

    def setUp(self):
        self.enum_original = original_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['phones'].message_type.fields_by_name['type'].enum_type
        self.enum_update = update_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['phones'].message_type.fields_by_name['type'].enum_type

    def tearDown(self):
        FindingContainer.reset()

    def enumRemoval(self):
        EnumComparator(self.enum_original, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'An Enum PhoneType is removed')
        self.assertEqual(finding.category.name, 'ENUM_REMOVAL')

    def enumAddition(self):
        EnumComparator(None, self.enum_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A new Enum PhoneTypeUpdate is added.')
        self.assertEqual(finding.category.name, 'ENUM_ADDITION')
    
    def enumNameChange(self):
        EnumComparator(self.enum_original, self.enum_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'Name of the Enum is changed, the original is PhoneType, but the updated is PhoneTypeUpdate')
        self.assertEqual(finding.category.name, 'ENUM_NAME_CHANGE')
            
    def oApiChange(self):
        EnumComparator(self.enum_update, self.enum_update).compare()
        self.assertEqual(len(FindingContainer.getAllFindings()), 0)

if __name__ == '__main__':
    unittest.main()
import unittest
import test.testdata.original_pb2 as original_version
import test.testdata.update_pb2 as update_version
from src.comparator.field_comparator import FieldComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory

class FieldComparatorTest(unittest.TestCase):

    def tearDown(self):
        FindingContainer.reset()

    def fieldRemoval(self):
        field_company_address = update_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['company_address']
        FieldComparator(field_company_address, None).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A Field company_address is removed')
        self.assertEqual(finding.category.name, 'FIELD_REMOVAL')

    def fieldAddition(self):
        field_married = update_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['married']
        FieldComparator(None, field_married).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'A new Field married is added.')
        self.assertEqual(finding.category.name, 'FIELD_ADDITION')

    def typeChange(self):
        field_id_original = original_version.DESCRIPTOR.message_types_by_name["Person"].fields[1]
        field_id_update = update_version.DESCRIPTOR.message_types_by_name["Person"].fields[1]
        FieldComparator(field_id_original, field_id_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'Type of the Field is changed, the original is TYPE_INT32, but the updated is TYPE_STRING')
        self.assertEqual(finding.category.name, 'FIELD_TYPE_CHANGE')

    def repeatedLabelChange(self):
        field_phones_original = original_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['phones']
        field_phones_update = update_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['phones']
        FieldComparator(field_phones_original, field_phones_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'Repeated state of the Field is changed, the original is LABEL_REPEATED, but the updated is LABEL_OPTIONAL')
        self.assertEqual(finding.category.name, 'FIELD_REPEATED_CHANGE')

    def nameChange(self):
        field_email_original = original_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['email']
        field_email_update = update_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['email_address']
        FieldComparator(field_email_original, field_email_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'Name of the Field is changed, the original is email, but the updated is email_address')
        self.assertEqual(finding.category.name, 'FIELD_NAME_CHANGE')

    def moveExistingFieldOutofOneof(self):
        field_email_original = original_version.DESCRIPTOR.message_types_by_name["AddressBook"].fields_by_name['deprecated']
        field_email_update = update_version.DESCRIPTOR.message_types_by_name["AddressBook"].fields_by_name['deprecated']
        FieldComparator(field_email_original, field_email_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'The Field deprecated is moved out of one-of')
        self.assertEqual(finding.category.name, 'FIELD_ONEOF_REMOVAL')

    def moveExistingFieldIntoOneof(self):
        field_email_original = original_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['home_address']
        field_email_update = update_version.DESCRIPTOR.message_types_by_name["Person"].fields_by_name['home_address']
        FieldComparator(field_email_original, field_email_update).compare()
        finding = FindingContainer.getAllFindings()[0]
        self.assertEqual(finding.message, 'The Field home_address is moved into one-of')
        self.assertEqual(finding.category.name, 'FIELD_ONEOF_ADDITION')

if __name__ == '__main__':
    unittest.main()
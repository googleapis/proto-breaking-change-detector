from google.protobuf.descriptor_pb2 import DescriptorProto
from src.comparator.field_comparator import FieldComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory

class DescriptorComparator:
    def __init__ (
        self, 
        message_original: DescriptorProto, 
        message_update: DescriptorProto):
            self.message_original = message_original
            self.message_update = message_update

    def compare(self):
        self._compare(self.message_original, self.message_update)
    
    def _compare(self, message_original, message_update):
        # 1. If original message is None, then a new message is added.
        if self.message_original is None:
            msg = 'A new message {} is added.'.format(self.message_update.name)
            FindingContainer.addFinding(FindingCategory.MESSAGE_ADDITION, "", msg, False)
            return
        # 2. If updated message is None, then the original message is removed.
        if self.message_update is None:
            msg = 'A message {} is removed'.format(self.message_original.name)
            FindingContainer.addFinding(FindingCategory.MESSAGE_REMOVAL, "", msg, True)
            return

        # 3. Check breaking changes in each fields. Note: Fields are identified by number, not by name.
        # Descriptor.fields_by_number (dict int -> FieldDescriptor) indexed by number.
        if message_original.fields_by_number or message_update.fields_by_number:
            self._compareNestedFields(message_original.fields_by_number, message_update.fields_by_number)
        
        # 4. Check breaking changes in nested message.
        # Descriptor.nested_types_by_name (dict str -> Descriptor) indexed by name.
        # Recursively call _compare for nested message type comparison.
        if (message_original.nested_types_by_name or message_update.nested_types_by_name):
            self._compareNestedMessages(message_original.nested_types_by_name, message_update.nested_types_by_name)

        # 5. TODO(xiaozhenliu): check `google.api.resource` annotation.     

    def _compareNestedFields(self, fieldsDict_original, fieldsDict_update):
        fieldsUnique_original = list(set(fieldsDict_original.keys()) - set(fieldsDict_update.keys()))
        fieldsUnique_update = list(set(fieldsDict_update.keys()) - set(fieldsDict_original.keys()))
        fieldsIntersaction = list(set(fieldsDict_original.keys()) & set(fieldsDict_update.keys()))
        
        for fieldNumber in fieldsUnique_original:
            FieldComparator(fieldsDict_original[fieldNumber], None).compare()
        for fieldNumber in fieldsUnique_update:
            FieldComparator(None, fieldsDict_update[fieldNumber]).compare()
        for fieldNumber in fieldsIntersaction:
            FieldComparator(fieldsDict_original[fieldNumber], fieldsDict_update[fieldNumber]).compare()
    
    def _compareNestedMessages(self, nestedMsgDict_original, nestedMsgDict_update):
        msgUnique_original = list(set(nestedMsgDict_original.keys()) - set(nestedMsgDict_update.keys()))
        msgUnique_update = list(set(nestedMsgDict_update.keys()) - set(nestedMsgDict_original.keys()))
        msgIntersaction = list(set(nestedMsgDict_original.keys()) & set(nestedMsgDict_update.keys()))

        for msgName in msgUnique_original:
            self._compare(nestedMsgDict_original[msgName], None)
        for msgName in msgUnique_update:
            self._compare(None, nestedMsgDict_update[msgName])
        for msgName in msgIntersaction:
            self._compare(nestedMsgDict_original[msgName], nestedMsgDict_update[msgName])

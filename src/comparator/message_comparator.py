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
        # TODO(xiaozhenliu): check existing fields that have been moved into/outof oneof.
        # While the oneof_index of every field is 0, which cannot be distinguished.
        if message_original.field or message_update.field:
            self._compareNestedFields(
                {f.number: f for f in message_original.field}, 
                {f.number: f for f in message_update.field})
        
        # 4. Check breaking changes in nested message.
        # Descriptor.nested_types_by_name (dict str -> Descriptor) indexed by name.
        # Recursively call _compare for nested message type comparison.
        if message_original.nested_type or message_update.nested_type:
            self._compareNestedMessages(
                {m.name: m for m in message_original.nested_type}, 
                {m.name: m for m in message_update.nested_type})

        # 5. TODO(xiaozhenliu): check `google.api.resource` annotation.     

    def _compareNestedFields(self, fields_dict_original, fields_dict_update):
        fields_unique_original = list(set(fields_dict_original.keys()) - set(fields_dict_update.keys()))
        fields_unique_update = list(set(fields_dict_update.keys()) - set(fields_dict_original.keys()))
        fieldsIntersaction = list(set(fields_dict_original.keys()) & set(fields_dict_update.keys()))
        
        for fieldNumber in fields_unique_original:
            FieldComparator(fields_dict_original[fieldNumber], None).compare()
        for fieldNumber in fields_unique_update:
            FieldComparator(None, fields_dict_update[fieldNumber]).compare()
        for fieldNumber in fieldsIntersaction:
            FieldComparator(fields_dict_original[fieldNumber], fields_dict_update[fieldNumber]).compare()
    
    def _compareNestedMessages(self, nested_msg_dict_original, nested_msg_dict_update):
        msg_unique_original = list(set(nested_msg_dict_original.keys()) - set(nested_msg_dict_update.keys()))
        msg_unique_update = list(set(nested_msg_dict_update.keys()) - set(nested_msg_dict_original.keys()))
        msgIntersaction = list(set(nested_msg_dict_original.keys()) & set(nested_msg_dict_update.keys()))

        for msgName in msg_unique_original:
            self._compare(nested_msg_dict_original[msgName], None)
        for msgName in msg_unique_update:
            self._compare(None, nested_msg_dict_update[msgName])
        for msgName in msgIntersaction:
            self._compare(nested_msg_dict_original[msgName], nested_msg_dict_update[msgName])

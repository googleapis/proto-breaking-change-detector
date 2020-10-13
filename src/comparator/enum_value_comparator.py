from google.protobuf.descriptor_pb2 import EnumValueDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory

class EnumValueComparator:
    def __init__ (
        self, 
        enum_value_original: EnumValueDescriptorProto, 
        enum_value_update: EnumValueDescriptorProto):
            self.enum_value_original = enum_value_original
            self.enum_value_update = enum_value_update

    def compare(self):
        # 1. If original EnumValue is None, then a new EnumValue is added.
        if self.enum_value_original is None:
           msg = 'A new EnumValue {} is added.'.format(self.enum_value_update.name)
           FindingContainer.addFinding(FindingCategory.ENUM_VALUE_ADDITION, "", msg, False)
        # 2. If updated EnumValue is None, then the original EnumValue is removed.
        elif self.enum_value_update is None:
           msg = ('An EnumValue {} is removed'.format(self.enum_value_original.name))
           FindingContainer.addFinding(FindingCategory.ENUM_VALUE_REMOVAL, "", msg, True)
        # 3. If both EnumValueDescriptors are existing, check if the name is changed.
        elif self.enum_value_original.name != self.enum_value_update.name:
           msg = ('Name of the EnumValue is changed, the original is {}, but the updated is {}'.format(self.enum_value_original.name, self.enum_value_update.name))
           FindingContainer.addFinding(FindingCategory.ENUM_VALUE_NAME_CHANGE, "", msg, True)

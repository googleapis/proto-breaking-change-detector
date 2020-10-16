from google.protobuf.descriptor_pb2 import EnumValueDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class EnumValueComparator:
    def __init__(
        self,
        enum_value_original: EnumValueDescriptorProto,
        enum_value_update: EnumValueDescriptorProto,
    ):
        self.enum_value_original = enum_value_original
        self.enum_value_update = enum_value_update

    def compare(self):
        # 1. Original EnumValue is None, then a new EnumValue is added.
        if self.enum_value_original is None:
            msg = f"A new EnumValue {self.enum_value_update.name} is added."
            FindingContainer.addFinding(
                FindingCategory.ENUM_VALUE_ADDITION, "", msg, False
            )
        # 2. Updated EnumValue is None, then the original EnumValue is removed.
        elif self.enum_value_update is None:
            msg = f"An EnumValue {self.enum_value_original.name} is removed"
            FindingContainer.addFinding(
                FindingCategory.ENUM_VALUE_REMOVAL, "", msg, True
            )
        # 3. Both EnumValueDescriptors are existing, check if the name
        # is changed.
        elif self.enum_value_original.name != self.enum_value_update.name:
            msg = "Name of the EnumValue is changed, the original is {}, but the updated is {}".format(
                self.enum_value_original.name, self.enum_value_update.name
            )
            FindingContainer.addFinding(
                FindingCategory.ENUM_VALUE_NAME_CHANGE, "", msg, True
            )

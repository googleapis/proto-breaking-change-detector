from google.protobuf.descriptor_pb2 import EnumDescriptorProto
from src.comparator.enum_value_comparator import EnumValueComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory


class EnumComparator:
    def __init__(
        self, enum_original: EnumDescriptorProto, enum_update: EnumDescriptorProto
    ):
        self.enum_original = enum_original
        self.enum_update = enum_update

    def compare(self):
        # 1. If original EnumDescriptor is None, then a new
        # EnumDescriptor is added.
        if self.enum_original is None:
            msg = "A new Enum {} is added.".format(self.enum_update.name)
            FindingContainer.addFinding(FindingCategory.ENUM_ADDITION, "", msg, False)

        # 2. If updated EnumDescriptor is None, then the original
        # EnumDescriptor is removed.
        elif self.enum_update is None:
            msg = "An Enum {} is removed".format(self.enum_original.name)
            FindingContainer.addFinding(FindingCategory.ENUM_REMOVAL, "", msg, True)

        # 3. If both EnumDescriptors are existing, check if the name is changed.
        elif self.enum_original.name != self.enum_update.name:
            msg = f"Name of the Enum is changed, the original is {self.enum_original.name}, but the updated is {self.enum_update.name}"
            FindingContainer.addFinding(FindingCategory.ENUM_NAME_CHANGE, "", msg, True)

        # 4. If the EnumDescriptors have the same name, check the values
        # of them stay the same. Enum values are identified by number,
        # not by name.
        else:
            enum_values_dict_original = {x.number: x for x in self.enum_original.value}
            enum_values_dict_update = {x.number: x for x in self.enum_update.value}
            enum_values_keys_set_original = set(enum_values_dict_original.keys())
            enum_values_keys_set_update = set(enum_values_dict_update.keys())
            # Compare Enum values that only exist in original version
            for number in enum_values_keys_set_original - enum_values_keys_set_update:
                EnumValueComparator(enum_values_dict_original[number], None).compare()
            # Compare Enum values that only exist in update version
            for number in enum_values_keys_set_update - enum_values_keys_set_original:
                EnumValueComparator(None, enum_values_dict_update[number]).compare()
            # Compare Enum values that exist both in original and update versions
            for number in enum_values_keys_set_original & enum_values_keys_set_update:
                EnumValueComparator(
                    enum_values_dict_original[number], enum_values_dict_update[number]
                ).compare()

from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory
import google.api.resource_pb2 as pb2
import google.protobuf.descriptor_pb2 as descriptor_pb2

class FieldComparator:
    def __init__ (
        self, 
        field_original: FieldDescriptorProto, 
        field_update: FieldDescriptorProto):
            self.field_original = field_original
            self.field_update = field_update

    def compare(self):
        # 1. If original FieldDescriptor is None, then a new FieldDescriptor is added.
        if self.field_original is None:
            msg = 'A new Field {} is added.'.format(self.field_update.name)
            FindingContainer.addFinding(FindingCategory.FIELD_ADDITION, "", msg, False)
            return

        # 2. If updated FieldDescriptor is None, then the original FieldDescriptor is removed.
        if self.field_update is None:
            msg = 'A Field {} is removed'.format(self.field_original.name)
            FindingContainer.addFinding(FindingCategory.FIELD_REMOVAL, "", msg, True)
            return

        # 3. If both FieldDescriptors are existing, check if the name is changed.
        if self.field_original.name != self.field_update.name:
            msg = 'Name of the Field is changed, the original is {}, but the updated is {}'.format(self.field_original.name, self.field_update.name)
            FindingContainer.addFinding(FindingCategory.FIELD_NAME_CHANGE, "", msg, True)
            return

        # 4. If the EnumDescriptors have the same name, check if the repeated state of them stay the same.
        if self.field_original.label != self.field_update.label:
            option_original = FieldDescriptorProto().Label.Name(self.field_original.label)
            option_update = FieldDescriptorProto().Label.Name(self.field_update.label)
            msg = 'Repeated state of the Field is changed, the original is {}, but the updated is {}'.format(option_original, option_update)
            FindingContainer.addFinding(FindingCategory.FIELD_REPEATED_CHANGE, "", msg, True)

        # 5. If the EnumDescriptors have the same repeated state, check if the type of them stay the same.
        if self.field_original.type != self.field_update.type:
            type_original = FieldDescriptorProto().Type.Name(self.field_original.type)
            type_update = FieldDescriptorProto().Type.Name(self.field_update.type)
            msg = 'Type of the Field is changed, the original is {}, but the updated is {}'.format(type_original, type_update)
            FindingContainer.addFinding(FindingCategory.FIELD_TYPE_CHANGE, "", msg, True)

        # 6. Check the existing field is moved out of one-of or moved into one-of .
        if self.field_original.containing_oneof != self.field_update.containing_oneof:
            if self.field_original.containing_oneof != None:
                msg = 'The Field {} is moved out of one-of'.format(self.field_original.name)
                FindingContainer.addFinding(FindingCategory.FIELD_ONEOF_REMOVAL, "", msg, True)
            else:
                msg = 'The Field {} is moved into one-of'.format(self.field_update.name)
                FindingContainer.addFinding(FindingCategory.FIELD_ONEOF_ADDITION, "", msg, True)
                
        # 7. Check `google.api.resource_reference` annotation.
        # TODO(xiaozhenliu): annotation is removed, but the using file-level resource is added to the message.
        # This should not be taken as breaking change.
        # if (self.fieldDescriptor_original.options != None) and (self.fieldDescriptor_original.options['google.api.resource_reference'] != None):
        #     print(pb2.DESCRIPTOR.message_types_by_name['ResourceReference'].fields[0])
        #     print(FieldDescriptorProto.options.HasExtension)
        #     print(descriptor_pb2.FieldOptions.DESCRIPTOR.message_types_by_name['ResourceReference'])


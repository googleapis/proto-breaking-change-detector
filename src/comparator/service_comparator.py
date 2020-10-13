from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.descriptor_pb2 import MethodDescriptorProto
from src.comparator.field_comparator import FieldComparator
from src.comparator.message_comparator import DescriptorComparator
from src.findings.finding_container import FindingContainer
from src.findings.utils import FindingCategory

class ServiceComparator:
    def __init__ (
        self, 
        service_original: ServiceDescriptorProto, 
        service_update: ServiceDescriptorProto):
            self.service_original = service_original
            self.service_update = service_update

    def compare(self):
        # 1. If original service is None, then a new service is added.
        if self.service_original is None:
            msg = 'A new service {} is added.'.format(self.service_update.name)
            FindingContainer.addFinding(FindingCategory.SERVICE_ADDITION, "", msg, False)
            return
        # 2. If updated service is None, then the original service is removed.
        if self.service_update is None:
            msg = 'A service {} is removed'.format(self.service_original.name)
            FindingContainer.addFinding(FindingCategory.SERVICE_REMOVAL, "", msg, True)
            return

        # 3. TODO(xiaozhenliu): method_signature annotation
        # 4. TODO(xiaozhenliu): LRO operation_info annotation
        # 5. TODO(xiaozhenliu): google.api.http annotation
        # 6. Check the methods list
        self._compareRpcMethods(self.service_original, self.service_update)


    def _compareRpcMethods(self, service_original, service_update):
        methods_original = {x.name: x for x in service_original.method} 
        methods_update = {x.name: x for x in service_update.method} 
        # 6.1 An RPC method is removed.
        for name in list(set(methods_original.keys()) - set(methods_update.keys())):
            msg = 'An rpc method {} is removed'.format(name)
            FindingContainer.addFinding(FindingCategory.METHOD_REMOVAL, "", msg, True)
        # 6.2 An RPC method is added.
        for name in list(set(methods_original.keys()) - set(methods_update.keys())):
            msg = 'An rpc method {} is added'.format(name)
            FindingContainer.addFinding(FindingCategory.METHOD_ADDTION, "", msg, False)
        for name in list(set(methods_original.keys()) & set(methods_update.keys())):
            method_original = methods_original[name]
            method_update = methods_update[name]
            # 6.3 The request type of an RPC method is changed.
            if method_original.input_type.name != method_update.input_type.name:
                msg = 'Input type of method {} is changed from {} to {}'.format(
                    name,
                    method_original.input_type.name,
                    method_update.input_type.name)
                FindingContainer.addFinding(FindingCategory.METHOD_INPUT_TYPE_CHANGE, "", msg, True)
            # 6.4 The request type of an RPC method is changed.
            if method_original.output_type.name != method_update.output_type.name:
                msg = 'Output type of method {} is changed from {} to {}'.format(
                    name,
                    method_original.output_type.name,
                    method_update.output_type.name)
                FindingContainer.addFinding(FindingCategory.METHOD_RESPONSE_TYPE_CHANGE, "", msg, True)
            # 6.5 The request streaming state of an RPC method is changed.
            if method_original.client_streaming != method_update.client_streaming:
                msg = 'The request streaming type of method {} is changed'.format(name)
                FindingContainer.addFinding(FindingCategory.METHOD_CLIENT_STREAMING_CHANGE, "", msg, True)
            # 6.6 The response streaming state of an RPC method is changed.
            if method_original.server_streaming != method_update.server_streaming:
                msg = 'The response streaming type of method {} is changed'.format(name)
                FindingContainer.addFinding(FindingCategory.METHOD_SERVER_STREAMING_CHANGE, "", msg, True)
            # 6.7 The paginated response of an RPC method is changed.
            if self._isPaginatedResponse(method_original) != self._isPaginatedResponse(method_update):
                msg = 'The paginated response of method {} is changed'.format(name)
                FindingContainer.addFinding(FindingCategory.METHOD_PAGINATED_RESPONSE_CHANGE, "", msg, True)

    def _isPaginatedResponse(
        self, 
        method: MethodDescriptorProto) -> bool:
        # (AIP 158) The response must not be a streaming response.
        if method.server_streaming:
            return False
        responseMsg = method.output_type
        # API must provide a `string next_page_token` field.
        if ('next_page_token' not in responseMsg.fields_by_name) or responseMsg.fields_by_name['next_page_token'].type != 9:
            return False
        # The field containing pagination results should be the first field in the message and have a field number of 1. 
        # It should be a repeated field containing a list of resources constituting a single page of results.
        if responseMsg.fields_by_number[1].label != 3:
            return False
        return True


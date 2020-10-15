import subprocess
import os
from google.protobuf import descriptor_pb2 as desc

class UnittestInvoker:
    _CURRENT_DIR = os.getcwd()
    _PROTOS_DIR = os.path.join(_CURRENT_DIR, 'test/testdata/protos/example/')
    _PROTOC = 'protoc'

    def __init__(
        self, 
        proto_files: [], 
        descriptor_set_file: str, 
        api_common_protos = False):
        self.proto_files = proto_files
        self.descriptor_set_file = descriptor_set_file
        self.api_common_protos = api_common_protos

    def run(self) -> desc.FileDescriptorSet:
        protoc_command = [self._PROTOC, f'--proto_path={self._PROTOS_DIR}']
        descriptor_set_output = os.path.join(self._PROTOS_DIR, self.descriptor_set_file)
        protoc_command.append(f'-o{descriptor_set_output}')
        for proto_file in self.proto_files:
            file_path = os.path.join(self._PROTOS_DIR, proto_file)
            protoc_command.append(file_path)

        # Run protoc command to get file that contains serialized data of proto files.
        process = subprocess.run(protoc_command)
        if process.returncode != 0:
            raise _ProtocInvokerException(f'Protoc commnand to invoke unit test fails: {protoc_command}')
        # Create FileDescriptorSet from the serialized data.
        desc_set = desc.FileDescriptorSet()
        with open(descriptor_set_output, "rb") as file:
            desc_set.ParseFromString(file.read())
        return desc_set

    def cleanup(self):
        # Remove the generated pb file once unit test is finished.
        descriptor_set_output = os.path.join(self._PROTOS_DIR, self.descriptor_set_file)
        if os.path.exists(descriptor_set_output):
            process = subprocess.run(['rm', descriptor_set_output])

class _ProtocInvokerException(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

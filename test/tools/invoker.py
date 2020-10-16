import subprocess
import os
from google.protobuf import descriptor_pb2 as desc


class UnittestInvoker:
    # This invoker is a wrapper of protoc command.
    # It takes in protoc command arguments (e.g. proto files,
    # descriptor_set_out and proto directories), executes the command
    # and cleans up the generated descriptor_set file.
    _CURRENT_DIR = os.getcwd()
    _PROTOS_DIR = os.path.join(_CURRENT_DIR, 'test/testdata/protos/example/')
    _PROTOC = 'protoc'

    def __init__(
            self,
            proto_files: [],
            descriptor_set_file: str,
            api_common_protos=False):
        self.proto_files = proto_files
        self.descriptor_set_file = descriptor_set_file
        # This arg is not used right now, but later on if we need api-common-protos
        # as dependency to run tests, we can enable this argument to include the protos.
        self.api_common_protos = api_common_protos

    def run(self) -> desc.FileDescriptorSet:
        # Construct the protoc command with proper argument prefix.
        protoc_command = [self._PROTOC, f'--proto_path={self._PROTOS_DIR}']
        descriptor_set_output = os.path.join(
            self._PROTOS_DIR, self.descriptor_set_file)
        protoc_command.append(f'-o{descriptor_set_output}')
        protoc_command.extend(os.path.join(self._PROTOS_DIR, pf)
                              for pf in self.proto_files)

        # Run protoc command to get pb file that contains serialized data of
        # the proto files.
        process = subprocess.run(protoc_command)
        if process.returncode != 0:
            raise _ProtocInvokerException(
                f'Protoc commnand to invoke unit test fails: {protoc_command}')
        # Create FileDescriptorSet from the serialized data.
        desc_set = desc.FileDescriptorSet()
        with open(descriptor_set_output, "rb") as f:
            desc_set.ParseFromString(f.read())
        return desc_set

    def cleanup(self):
        # Remove the generated pb file once unit test is finished.
        descriptor_set_output = os.path.join(
            self._PROTOS_DIR, self.descriptor_set_file)
        if os.path.exists(descriptor_set_output):
            subprocess.run(['rm', descriptor_set_output])


class _ProtocInvokerException(Exception):
    pass

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
from subprocess import PIPE
import os
from typing import Sequence
from google.protobuf import descriptor_pb2 as desc


class Loader:
    # This loader is a wrapper of protoc command.
    # It takes in protoc command arguments (e.g. proto files,
    # descriptor_set_out and proto directories), executes the command
    # and cleans up the generated descriptor_set file.
    # This also works as the **temporary** solution of loading FileDescriptorSet
    # from API definition files that ussers pass in from the command line.
    _CURRENT_DIR = os.getcwd()
    PROTOC_BINARY = os.path.join(_CURRENT_DIR, "test/tools/protoc")
    COMMON_PROTOS_DIR = os.path.join(_CURRENT_DIR, "api-common-protos")
    PROTOBUF_PROTOS_DIR = os.path.join(_CURRENT_DIR, "protobuf/src")

    def __init__(
        self,
        proto_defintion_dirs,
        descriptor_set,
        proto_files=None,
    ):
        self.proto_defintion_dirs = proto_defintion_dirs
        self.descriptor_set = descriptor_set
        self.proto_files = (
            proto_files if proto_files else self._get_proto_files(proto_defintion_dirs)
        )

    def get_descriptor_set(self) -> desc.FileDescriptorSet:
        desc_set = desc.FileDescriptorSet()
        # If users pass in descriptor set file directly, we
        # can skip running the protoc command.
        if self.descriptor_set:
            with open(self.descriptor_set, "rb") as f:
                desc_set.ParseFromString(f.read())
            return desc_set
        # Construct the protoc command with proper argument prefix.
        protoc_command = [self.PROTOC_BINARY]
        for directory in self.proto_defintion_dirs:
            protoc_command.append(f"--proto_path={directory}")
        protoc_command.append(f"--proto_path={self.COMMON_PROTOS_DIR}")
        protoc_command.append(f"--proto_path={self.PROTOBUF_PROTOS_DIR}")
        protoc_command.append("-o/dev/stdout")
        protoc_command.append("--include_source_info")
        # Include the imported dependencies.
        protoc_command.append("--include_imports")
        protoc_command.extend(pf for pf in self.proto_files)

        # Run protoc command to get pb file that contains serialized data of
        # the proto files.
        process = subprocess.run(protoc_command, stdout=PIPE)
        if process.returncode != 0:
            raise _ProtocInvokerException(
                f"Protoc command to load the descriptor set fails: {protoc_command}"
            )
        # Create FileDescriptorSet from the serialized data.
        desc_set.ParseFromString(process.stdout)
        return desc_set

    def _get_proto_files(self, proto_definition):
        if not proto_definition:
            return None
        # Get all the files that have extension `.proto` in proto_dirs.
        proto_files = [
            fname
            for directory in proto_definition
            for fname in os.listdir(directory)
            if os.path.splitext(fname)[1] == ".proto"
        ]
        return proto_files


class _ProtocInvokerException(Exception):
    pass

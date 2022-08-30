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

import logging
import shutil
import os
import subprocess
from subprocess import CalledProcessError, PIPE
from typing import Optional, Sequence
import tempfile

from google.protobuf import descriptor_pb2 as desc
from grpc_tools import protoc


class Loader:
    # This loader is a wrapper of protoc command.
    # It takes in protoc command arguments (e.g. proto files,
    # descriptor_set_out and proto directories), executes the command
    # and cleans up the generated descriptor_set file.
    # This also works as the **temporary** solution of loading FileDescriptorSet
    # from API definition files that ussers pass in from the command line.
    _CURRENT_DIR = os.getcwd()
    PROTOBUF_PROTOS_DIR = os.path.join(_CURRENT_DIR, "protobuf/src")
    GRPC_TOOLS_PROTOC = "grpc_tools.protoc"

    def __init__(
        self,
        proto_definition_dirs: Sequence[str],
        proto_files: Sequence[str],
        descriptor_set: str,
        include_source_code: bool = True,
        protoc_binary: Optional[str] = None,
        local_protobuf: bool = True,
    ):
        self.proto_definition_dirs = proto_definition_dirs
        self.descriptor_set = descriptor_set
        self.proto_files = proto_files
        self.include_source_code = include_source_code
        self.protoc_binary = protoc_binary or self.GRPC_TOOLS_PROTOC
        self.local_protobuf = local_protobuf

    def get_descriptor_set(self) -> desc.FileDescriptorSet:
        local_dir = os.getcwd()
        desc_set = desc.FileDescriptorSet()
        # If users pass in descriptor set file directly, we
        # can skip running the protoc command.
        if self.descriptor_set:
            with open(self.descriptor_set, "rb") as f:
                desc_set.ParseFromString(f.read())
            return desc_set
        # Construct the protoc command with proper argument prefix.
        protoc_command = [self.protoc_binary]
        for directory in self.proto_definition_dirs:
            if self.local_protobuf:
                protoc_command.append(f"--proto_path={directory}")
            else:
                protoc_command.append(f"--proto_path={local_dir}/{directory}")
        if self.local_protobuf:
            protoc_command.append(f"--proto_path={self.PROTOBUF_PROTOS_DIR}")
        if self.include_source_code:
            protoc_command.append("--include_source_info")
        # Include the imported dependencies.
        protoc_command.append("--include_imports")
        if self.local_protobuf:
            protoc_command.extend(pf for pf in self.proto_files)
        else:
            protoc_command.extend((local_dir + "/" + pf) for pf in self.proto_files)

        # Run protoc command to get pb file that contains serialized data of
        # the proto files.
        if self.protoc_binary == self.GRPC_TOOLS_PROTOC:
            fd, path = tempfile.mkstemp()
            protoc_command.append("--descriptor_set_out=" + path)
            # Use grpcio-tools.protoc to compile proto files
            if protoc.main(protoc_command) != 0:
                raise _ProtocInvokerException(
                    f"Protoc command to load the descriptor set fails. {protoc_command}"
                )
            else:
                # Create FileDescriptorSet from the serialized data.
                with open(fd, "rb") as f:
                    desc_set.ParseFromString(f.read())
                return desc_set
        try:
            protoc_command.append("-o/dev/stdout")
            union_command = " ".join(protoc_command)
            logging.info(f"Run protoc command: {union_command}")
            process = subprocess.run(
                union_command, shell=True, stdout=PIPE, stderr=PIPE
            )
            logging.info(f"Check the process output is not empty:")
            logging.info(bool(process.stdout))
            if process.returncode != 0:
                raise _ProtocInvokerException(
                    f"Protoc command to load the descriptor set fails. {union_command}, error: {process.stderr}"
                )
        except (CalledProcessError, FileNotFoundError) as e:
            logging.info(f"Call process error: {e}")

        # Create FileDescriptorSet from the serialized data.
        desc_set.ParseFromString(process.stdout)
        return desc_set


class _ProtocInvokerException(Exception):
    pass

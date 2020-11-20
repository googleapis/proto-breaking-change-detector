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

import os


class Options:
    """Build the options for protoc command arguments.

    proto_definition_dirs: Required if descriptor_set_file_path is not set.
                           The directories where we should find the proto files,
                           including proto definition files and their dependencies.
                           Comma separated string. It can also be FileDescriptorSet object
                           compiled by protocol compiler.
    descriptor_set_file_path: The path to the compiled descriptor set file.
    package_prefixes: Optional.The package prefixes of the proto definition files,
                      so that in the comparators, we can safely skip the
                      dependency protos if needed. Comma separated string.
    human_readable_message: Optional flag. Enable printing the human-readable
                            messages if true. Default value if false.
    output_json_path: Optional. The path of the findings json file. If not specify,
                      we will create a json for the users which is in
                      `$root/detected_breaking_changes.json`.
    """

    def __init__(
        self,
        original_api_definition_dirs: str,
        update_api_definition_dirs: str,
        original_descriptor_set_file_path: str,
        update_descriptor_set_file_path: str,
        package_prefixes: str = None,
        human_readable_message: bool = False,
        output_json_path: str = None,
    ):
        self.original_api_definition_dirs = self._get_proto_dirs(
            original_api_definition_dirs
        )
        self.update_api_definition_dirs = self._get_proto_dirs(
            update_api_definition_dirs
        )
        self.original_descriptor_set_file_path = original_descriptor_set_file_path
        self.update_descriptor_set_file_path = update_descriptor_set_file_path
        # Check the arguments are valid for detection.
        if not self._valid_arguments():
            raise _InvalidArgumentsException(
                "Either directories of the proto definition files or path of the descriptor set files should be specified."
            )
        self.package_prefixes = self._get_package_prefixes(package_prefixes)
        self.human_readable_message = human_readable_message
        self.output_json_path = self._get_output_json_path(output_json_path)

    def use_proto_dirs(self) -> bool:
        # User pass in the directorirs of proto definition files as input.
        if not self.original_api_definition_dirs or not self.update_api_definition_dirs:
            return False
        return True

    def use_descriptor_set(self) -> bool:
        # User pass in the path of descriptor set files as input.
        if (
            not self.original_descriptor_set_file_path
            or not self.update_descriptor_set_file_path
        ):
            return False
        return True

    def _valid_arguments(self) -> bool:
        # Either directories of the proto definition files or path of 
        # the descriptor set files should be specified. And the pass in
        # directory or file path should be valid. Else return False.

        if not self.use_proto_dirs() and not self.use_descriptor_set():
            return False
        if self.use_proto_dirs():
            return self._check_valid_dirs(
                self.original_api_definition_dirs
            ) and self._check_valid_dirs(self.update_api_definition_dirs)
        return self._check_valid_file(
            self.original_descriptor_set_file_path
        ) and self._check_valid_file(self.update_descriptor_set_file_path)

    def _get_proto_dirs(self, arg):
        # Return an array of the proto directories or a descriptor set file path.
        if not arg:
            return None
        return arg.split(",")

    def _get_package_prefixes(self, prefixes):
        if not prefixes:
            return None
        return [prefix.strip() for prefix in prefixes.split(",")]

    def _get_output_json_path(self, path):
        # Return the path of json output file, use default path if not set.
        # Raise error if the specified path is not valid.
        if not path:
            return os.path.join(os.getcwd(), "detected_breaking_changes.json")
        elif not os.path.isfile(path):
            raise TypeError(f"The output_json_path {path} is not existing.")
        return path

    def _check_valid_dirs(self, dirs) -> bool:
        # Return True if the directories path are valid, else False.
        for directory in dirs:
            if not os.path.isdir(directory):
                raise TypeError(f"The directory {directory} is not existing.")
        return True

    def _check_valid_file(self, file) -> bool:
        # Return True if the file path is valid, else False.
        if not os.path.isfile(file):
            raise TypeError(f"The file {file} is not existing.")
        return True


class _InvalidArgumentsException(Exception):
    pass

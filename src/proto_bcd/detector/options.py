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
from typing import Optional


class Options:
    """Build the options for protoc command arguments.

    proto_definition_dirs: Required if descriptor_set_file_path is not set.
                           Specify the directories in which to search for the
                           original proto API definition files and imports.
                           Comma separated string.
    proto_files: Required if descriptor_set_file_path is not set.
                 The path to the files of proto API definition files.
                 Comma separated string.
    descriptor_set_file_path: The path to the compiled descriptor set file.
    human_readable_message: Optional flag. Enable printing the human-readable
                            messages if true. Default value if false.
    output_json_path: Optional. The path of the findings json file. If not specify,
                      we will create a json for the users which is in
                      `$root/detected_breaking_changes.json`.
    line_numbers: Show line numbers from the human readable output. True by default.
    all_changes: Show all changes, not only breaking changes. False by default.
    """

    def __init__(
        self,
        original_api_definition_dirs: str,
        update_api_definition_dirs: str,
        original_proto_files: str,
        update_proto_files: str,
        original_descriptor_set_file_path: str,
        update_descriptor_set_file_path: str,
        human_readable_message: bool = False,
        output_json_path: Optional[str] = None,
        line_numbers: bool = True,
        all_changes: bool = False,
    ):
        self.original_api_definition_dirs = self._get_arg_arr(
            original_api_definition_dirs
        )
        self.update_api_definition_dirs = self._get_arg_arr(update_api_definition_dirs)
        self.original_proto_files = self._get_arg_arr(original_proto_files)
        self.update_proto_files = self._get_arg_arr(update_proto_files)
        self.original_descriptor_set_file_path = original_descriptor_set_file_path
        self.update_descriptor_set_file_path = update_descriptor_set_file_path
        # Check the arguments are valid for detection.
        if not self._valid_arguments():
            raise _InvalidArgumentsException(
                "Either directories of the proto definition files or path of the descriptor set files should be specified."
            )
        self.human_readable_message = human_readable_message
        self.output_json_path = self._get_output_json_path(output_json_path)
        self.line_numbers = line_numbers
        self.all_changes = all_changes

    def use_proto_dirs(self) -> bool:
        # User pass in the directories of proto definition files as input.
        if (
            self.original_api_definition_dirs
            and self.original_proto_files
        ):
            return True
        return False

    def use_descriptor_set(self) -> bool:
        # User pass in the path of descriptor set files as input.
        if (
            self.original_descriptor_set_file_path
            and self.update_descriptor_set_file_path
        ):
            return True
        return False

    def _valid_arguments(self) -> bool:
        # Either directories of the proto definition files or path of
        # the descriptor set files should be specified. And the pass in
        # directory or file path should be valid. Else return False.
        if not self.use_proto_dirs() and not self.use_descriptor_set():
            return False

        if self.use_proto_dirs():
            if not self._check_valid_dirs(self.original_api_definition_dirs):
                return False
            if not self.update_api_definition_dirs:
                # Allow args to not specify updated directories, as these
                # may have been deleted.
                return True
            return self._check_valid_dirs(self.update_api_definition_dirs)

        return self._check_valid_file(
            self.original_descriptor_set_file_path
        ) and self._check_valid_file(self.update_descriptor_set_file_path)

    def _get_arg_arr(self, args):
        # Return an array of the proto directories or a descriptor set file path.
        if not args:
            return None
        return [arg.strip() for arg in args.split(",")]

    def _get_output_json_path(self, path):
        # Return the path of json output file, use default path if not set.
        # Raise error if the specified path is not valid.
        if not path:
            return os.path.join(os.getcwd(), "detected_breaking_changes.json")
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

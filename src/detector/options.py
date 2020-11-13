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

    proto_dirs: Required. The directories where we should find the proto files,
                including proto definition files and their dependencies.
                Comma separated string.
    proto_files: Optional. Proto files list to pass in the protoc command.
                 If not specify, we will look up all the protos in the `proto_dirs`.
                 Comma separated string.
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
        proto_dirs_original: str,
        proto_dirs_update: str,
        package_prefixes: str = None,
        human_readable_message: bool = False,
        output_json_path: str = None,
    ):
        self.proto_dirs_original = self._get_proto_dirs(proto_dirs_original)
        self.proto_dirs_update = self._get_proto_dirs(proto_dirs_update)
        self.package_prefixes = self._get_package_prefixes(package_prefixes)
        self.human_readable_message = human_readable_message
        self.output_json_path = self._get_output_json_path(output_json_path)

    def _get_proto_dirs(self, proto_dirs):
        proto_dirs_arr = proto_dirs.split(",")
        if not proto_dirs_arr:
            return []
        for directory in proto_dirs_arr:
            if not os.path.isdir(directory):
                raise TypeError(f"The directory {directory} is not existing.")
        return proto_dirs_arr

    def _get_package_prefixes(self, prefixes):
        if not prefixes:
            return None
        return [prefix.strip() for prefix in prefixes.split(",")]

    def _get_output_json_path(self, path):
        if not path:
            return os.path.join(os.getcwd(), "detected_breaking_changes.json")
        elif not os.path.isfile(path):
            raise TypeError(f"The output_json_path {path} is not existing.")
        return path

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

import click
from src.detector.options import Options
from src.detector.loader import Loader
from src.detector.detector import Detector


@click.command()
@click.option(
    "--original_api_definition_dirs",
    help="The path to the directories of original proto API definition files.",
)
@click.option(
    "--update_api_definition_dirs",
    help="The path to the directories of update proto API definition files.",
)
@click.option(
    "--original_descriptor_set_file_path",
    help="The path to the original compiled descriptor set file.",
)
@click.option(
    "--update_descriptor_set_file_path",
    help="The path to the update compiled descriptor set file.",
)
@click.option(
    "--output_json_path",
    help="The file path for json output which contains all the breaking change findings. The default path is the current folder.",
)
@click.option(
    "--package_prefixes",
    default="",
    help="The prefixes for the package name of the API definition proto files.",
)
@click.option(
    "--human_readable_message",
    default=False,
    is_flag=True,
    help="Enable the human-readable message output if set to True. Default value is false.",
)
def detect(
    original_api_definition_dirs: str,
    update_api_definition_dirs: str,
    original_descriptor_set_file_path: str,
    update_descriptor_set_file_path: str,
    output_json_path: str,
    package_prefixes: str,
    human_readable_message: bool,
):
    """Detect the breaking changes of the original and updated versions of API definition files. """
    # 1. Read the stdin options and create the Options object for all the command args.
    # The detector accepts two types of the input:
    # a) proto API defintion files.
    # b) compiled FileDescriptorSet file which can be obtained by protocal compiler.
    options = Options(
        original_api_definition_dirs,
        update_api_definition_dirs,
        original_descriptor_set_file_path,
        update_descriptor_set_file_path,
        package_prefixes,
        human_readable_message,
        output_json_path,
    )
    # 3. Create protoc command (back up solution) to load the FileDescriptorSet.
    # It takes options, returns fileDescriptorSet.
    if options.use_descriptor_set():
        file_set_original = Loader(
            None, options.original_descriptor_set_file_path
        ).get_descriptor_set()
        file_set_update = Loader(
            None, options.update_descriptor_set_file_path
        ).get_descriptor_set()
    elif options.use_proto_dirs():
        file_set_original = Loader(
            options.original_api_definition_dirs, None
        ).get_descriptor_set()
        file_set_update = Loader(
            options.update_api_definition_dirs, None
        ).get_descriptor_set()
    # 4. Create the detector with two FileDescriptorSet and options.
    # It creates output_json file and prints human-readable message if the option is enabled.
    Detector(file_set_original, file_set_update, options).detect_breaking_changes()


if __name__ == "__main__":
    detect()

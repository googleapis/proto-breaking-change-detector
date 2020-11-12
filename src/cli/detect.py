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
import os


@click.command()
@click.argument(
    "original",
    # help="The directories for the original version proto API definition files, separate by commas.",
)
@click.argument(
    "update",
    # help="The directories for the updated version proto API definition files, separate by commas.",
)
@click.option(
    "--output_json_path",
    default=os.getcwd(),
    help="The file path for json output which contains all the breaking change findings. The default path is the current folder.",
)
@click.option(
    "--package_prefixes",
    default='',
    help="The file path for json output which contains all the breaking change findings. The default path is the current folder.",
)
@click.option(
    "--human_readable_message",
    default=False,
    is_flag=True,
    help="Enable the human-readable message output if set to True.",
)
def detect(
    original: str,
    update: str,
    output_json_path: str,
    package_prefixes: str,
    human_readable_message: bool,
):
    print(original)
    print(update)
    print(output_json_path)
    print(human_readable_message)


# 1. Readin the stdin options including [required] original_API_definition_dirs,
# update_API_definition_dirs, [optional] human-readable-message, output_json_file.
# 2. Create the options for all the command args. (options.Options.build())

# 3. Create protoc command (back up solution) to load the FileDescriptorSet.(loader.py)
# It takes options, returns fileDescriptorSet.

# 4. Create detector with two FileDescriptorSet and options.
# It returns output_json file and human-readable message based on options.


if __name__ == "__main__":
    detect()

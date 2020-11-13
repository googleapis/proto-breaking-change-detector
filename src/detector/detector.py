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
import json
import sys
from google.protobuf import descriptor_pb2 as desc
from src.detector.options import Options
from src.comparator.file_set_comparator import FileSetComparator
from src.comparator.wrappers import FileSet
from src.findings.finding_container import FindingContainer


class Detector:
    """Detect the breaking changes in the two versions of FileDescriptorSet"""

    def __init__(
        self,
        descriptor_set_original: desc.FileDescriptorSet,
        descriptor_set_update: desc.FileDescriptorSet,
        opts: Options,
    ):
        # Init FileSetComparator and compare the two FileDescriptorSet.
        FileSetComparator(
            FileSet(descriptor_set_original, opts.package_prefixes),
            FileSet(descriptor_set_update, opts.package_prefixes),
        ).compare()
        # Output json file of findings and human-readable messages if the
        # command line option is enabled.
        if not os.path.exists(opts.output_json_path):
            with open(opts.output_json_path, "w") as write_json_file:
                json.dump(FindingContainer.toDictArr(), write_json_file)

        if opts.human_readable_message:
            # Call toHumanReadableMessage() method once it is merged in.
            sys.stdout.write("Human Readable Message.")

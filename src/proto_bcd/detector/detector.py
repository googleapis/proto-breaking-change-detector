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

import json
import sys
from typing import Optional
from google.protobuf import descriptor_pb2 as desc
from proto_bcd.detector.options import Options
from proto_bcd.comparator.file_set_comparator import FileSetComparator
from proto_bcd.comparator.wrappers import FileSet
from proto_bcd.findings.finding_container import FindingContainer


class Detector:
    """Detect the breaking changes in the two versions of FileDescriptorSet"""

    def __init__(
        self,
        descriptor_set_original: desc.FileDescriptorSet,
        descriptor_set_update: desc.FileDescriptorSet,
        opts: Optional[Options] = None,
    ):
        self.descriptor_set_original = descriptor_set_original
        self.descriptor_set_update = descriptor_set_update
        self.opts = opts
        self.finding_container = FindingContainer()

    def _compare(self):
        # Init FileSetComparator and compare the two FileDescriptorSet.
        # Result is stored in self.finding_container, and printed to stdout if requested.
        comparator = FileSetComparator(
            FileSet(self.descriptor_set_original),
            FileSet(self.descriptor_set_update),
            self.finding_container,
        )
        comparator.compare()

        if self.opts and self.opts.output_json_path:
            # Output json file of findings and human-readable messages if the
            # command line option is enabled.
            with open(self.opts.output_json_path, "w") as write_json_file:
                json.dump(
                    self.finding_container.to_dict_arr(), write_json_file, indent=2
                )

        if self.opts and self.opts.human_readable_message:
            sys.stdout.write(
                self.finding_container.to_human_readable_message(
                    line_numbers=self.opts.line_numbers,
                    all_changes=self.opts.all_changes,
                )
            )

    def detect_breaking_changes(self):
        self._compare()
        return self.finding_container.get_actionable_findings()

    def detect_all_changes(self):
        self._compare()
        return self.finding_container.get_all_findings()

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

import unittest
import os
from src.detector.loader import Loader
from google.protobuf import descriptor_pb2


class LoaderTest(unittest.TestCase):
    _CURRENT_DIR = os.getcwd()

    def test_loader_proto_dirs(self):
        loader = Loader(
            [os.path.join(self._CURRENT_DIR, "test/testdata/protos/example/")],
            [
                os.path.join(
                    self._CURRENT_DIR, "test/testdata/protos/example/wrappers.proto"
                )
            ],
        )
        self.assertTrue(loader)
        self.assertEqual(
            loader.proto_defintion,
            [os.path.join(self._CURRENT_DIR, "test/testdata/protos/example/")],
        )
        self.assertEqual(
            loader.proto_files,
            [
                os.path.join(
                    self._CURRENT_DIR, "test/testdata/protos/example/wrappers.proto"
                )
            ],
        )
        self.assertTrue(loader.get_descriptor_set())
        self.assertTrue(
            isinstance(loader.get_descriptor_set(), descriptor_pb2.FileDescriptorSet)
        )

    def test_loader_descriptor_set(self):
        loader = Loader(
            os.path.join(
                self._CURRENT_DIR, "test/testdata/protos/enum/v1/enum_descriptor_set.pb"
            )
        )
        self.assertTrue(loader)
        self.assertEqual(
            loader.proto_defintion,
            os.path.join(
                self._CURRENT_DIR, "test/testdata/protos/enum/v1/enum_descriptor_set.pb"
            ),
        )
        self.assertFalse(loader.proto_files)
        self.assertTrue(loader.get_descriptor_set())
        self.assertTrue(
            isinstance(loader.get_descriptor_set(), descriptor_pb2.FileDescriptorSet)
        )


if __name__ == "__main__":
    unittest.main()

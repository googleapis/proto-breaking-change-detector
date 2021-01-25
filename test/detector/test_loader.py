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
    COMMON_PROTOS_DIR = os.path.join(os.getcwd(), "api-common-protos")
    
    def test_loader_args(self):
        loader = Loader(
            proto_defintion_dirs=None,
            proto_files=None,
            descriptor_set="//path/to/descriptor/set",
            include_source_code=False,
            protoc_binary="//path/to/protoc/binary",
            local_protobuf=False,
        )
        self.assertFalse(loader.include_source_code)
        self.assertFalse(loader.local_protobuf)
        self.assertEqual(loader.protoc_binary, "//path/to/protoc/binary")
        self.assertEqual(loader.descriptor_set, "//path/to/descriptor/set")


    def test_loader_proto_dirs(self):
        loader = Loader(
            proto_defintion_dirs=[
                os.path.join(self._CURRENT_DIR, "test/testdata/protos/example/"),
                self.COMMON_PROTOS_DIR,
            ],
            proto_files=[
                os.path.join(
                    self._CURRENT_DIR, "test/testdata/protos/example/wrappers.proto"
                )
            ],
            descriptor_set=None,
        )
        self.assertTrue(loader)
        self.assertEqual(
            loader.proto_defintion_dirs,
            [
                os.path.join(self._CURRENT_DIR, "test/testdata/protos/example/"),
                self.COMMON_PROTOS_DIR,
            ],
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
        self.assertIsInstance(
            loader.get_descriptor_set(), descriptor_pb2.FileDescriptorSet
        )

    def test_loader_descriptor_set(self):
        loader = Loader(
            proto_defintion_dirs=None,
            proto_files=None,
            descriptor_set=os.path.join(
                self._CURRENT_DIR, "test/testdata/protos/enum/v1/enum_descriptor_set.pb"
            ),
        )
        self.assertTrue(loader)
        self.assertEqual(
            loader.descriptor_set,
            os.path.join(
                self._CURRENT_DIR, "test/testdata/protos/enum/v1/enum_descriptor_set.pb"
            ),
        )
        self.assertFalse(loader.proto_files)
        self.assertTrue(loader.get_descriptor_set())
        self.assertIsInstance(
            loader.get_descriptor_set(), descriptor_pb2.FileDescriptorSet
        )


if __name__ == "__main__":
    unittest.main()

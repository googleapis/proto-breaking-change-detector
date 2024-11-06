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
from google.protobuf import descriptor_pb2

from proto_bcd.detector.loader import Loader, _ProtocInvokerException


class LoaderTest(unittest.TestCase):
    _CURRENT_DIR = os.getcwd()
    COMMON_PROTOS_DIR = os.path.join(os.getcwd(), "api-common-protos")

    def test_loader_args_default(self):
        loader = Loader(
            proto_definition_dirs=None,
            proto_files=None,
            descriptor_set="//path/to/descriptor/set",
        )
        self.assertTrue(loader.include_source_code)
        self.assertTrue(loader.local_protobuf)
        self.assertEqual(loader.protoc_binary, "grpc_tools.protoc")
        self.assertEqual(loader.descriptor_set, "//path/to/descriptor/set")
        self.assertFalse(loader.proto_definition_dirs)
        self.assertFalse(loader.proto_files)

    def test_loader_args_overwrite(self):
        loader = Loader(
            proto_definition_dirs=["dira", "dirb", "dirc"],
            proto_files=["a", "b", "c"],
            descriptor_set="//path/to/descriptor/set",
            include_source_code=False,
            protoc_binary="//path/to/protoc/binary",
            local_protobuf=False,
        )
        self.assertFalse(loader.include_source_code)
        self.assertFalse(loader.local_protobuf)
        self.assertEqual(loader.protoc_binary, "//path/to/protoc/binary")
        self.assertEqual(loader.proto_definition_dirs, ["dira", "dirb", "dirc"])
        self.assertEqual(loader.proto_files, ["a", "b", "c"])
        self.assertEqual(loader.descriptor_set, "//path/to/descriptor/set")

    def test_loader_proto_dirs(self):
        loader = Loader(
            proto_definition_dirs=[
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
            loader.proto_definition_dirs,
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

    def test_loader_proto_dirs_none(self):
        loader = Loader(
            proto_definition_dirs=None,
            proto_files=None,
            descriptor_set=None,
        )
        self.assertTrue(loader)
        self.assertFalse(loader.proto_definition_dirs)
        self.assertFalse(loader.proto_files)
        self.assertTrue(loader.get_descriptor_set())
        self.assertIsInstance(
            loader.get_descriptor_set(), descriptor_pb2.FileDescriptorSet
        )

    def test_loader_descriptor_set(self):
        loader = Loader(
            proto_definition_dirs=None,
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

    def test_loader_invalid_proto_compiler(self):
        loader = Loader(
            proto_definition_dirs=["dira", "dirb", "dirc"],
            proto_files=["a", "b", "c"],
            descriptor_set=None,
            protoc_binary="//invalid/proto/compiler",
        )
        self.assertTrue(loader)
        self.assertEqual(loader.protoc_binary, "//invalid/proto/compiler")
        with self.assertRaisesRegex(
            _ProtocInvokerException, "Protoc command to load the descriptor set fails."
        ):
            loader.get_descriptor_set()


if __name__ == "__main__":
    unittest.main()

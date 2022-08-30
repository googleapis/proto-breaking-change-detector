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
from unittest import mock
import os

from proto_bcd.detector.options import Options, _InvalidArgumentsException


class OptionsTest(unittest.TestCase):
    def test_options_proto_dirs_default(self):
        with mock.patch("os.path.isdir") as mocked_isdir:
            with mock.patch("os.path.isfile") as mocked_isfile:
                mocked_isdir.return_value = True
                mocked_isfile.return_value = True
                opts = Options(
                    original_api_definition_dirs="c,d",
                    update_api_definition_dirs="a,b",
                    original_proto_files="pf1, pf2",
                    update_proto_files="pf3, pf4",
                    original_descriptor_set_file_path=None,
                    update_descriptor_set_file_path=None,
                )
        self.assertEqual(opts.original_api_definition_dirs, ["c", "d"])
        self.assertEqual(opts.update_api_definition_dirs, ["a", "b"])
        self.assertEqual(opts.original_proto_files, ["pf1", "pf2"])
        self.assertEqual(opts.update_proto_files, ["pf3", "pf4"])
        # Default value for human_readable_message is False.
        self.assertFalse(opts.human_readable_message)
        # external dependencie is needed.
        self.assertEqual(opts.original_descriptor_set_file_path, None)
        self.assertEqual(opts.update_descriptor_set_file_path, None)
        self.assertTrue(opts.use_proto_dirs())
        self.assertFalse(opts.use_descriptor_set())
        # Use default json path if not set.
        self.assertEqual(
            opts.output_json_path,
            os.path.join(os.getcwd(), "detected_breaking_changes.json"),
        )

    def test_options_proto_dirs_custom(self):
        with mock.patch("os.path.isdir") as mocked_isdir:
            with mock.patch("os.path.isfile") as mocked_isfile:
                mocked_isdir.return_value = True
                mocked_isfile.return_value = True
                opts = Options(
                    original_api_definition_dirs="c,d",
                    update_api_definition_dirs="a,b",
                    original_proto_files="pf1, pf2",
                    update_proto_files="pf3, pf4",
                    original_descriptor_set_file_path=None,
                    update_descriptor_set_file_path=None,
                    human_readable_message=True,
                    output_json_path="mock_path.json",
                )
        self.assertEqual(opts.original_api_definition_dirs, ["c", "d"])
        self.assertEqual(opts.update_api_definition_dirs, ["a", "b"])
        # Strip the unneeded whitespaces.
        self.assertEqual(opts.original_proto_files, ["pf1", "pf2"])
        self.assertEqual(opts.update_proto_files, ["pf3", "pf4"])
        self.assertTrue(opts.human_readable_message)
        # Use custom json path if set.
        self.assertEqual(opts.output_json_path, "mock_path.json")

    def test_options_descriptor_set_file(self):
        with mock.patch("os.path.isfile") as mocked_isfile:
            mocked_isfile.return_value = True
            opts = Options(
                original_api_definition_dirs=None,
                update_api_definition_dirs=None,
                original_proto_files=None,
                update_proto_files=None,
                original_descriptor_set_file_path="descriptor_set_original.pb",
                update_descriptor_set_file_path="descriptor_set_udpate.pb",
                human_readable_message=True,
            )
        self.assertEqual(
            opts.original_descriptor_set_file_path, "descriptor_set_original.pb"
        )
        self.assertEqual(
            opts.update_descriptor_set_file_path, "descriptor_set_udpate.pb"
        )
        self.assertEqual(opts.original_api_definition_dirs, None)
        self.assertEqual(opts.update_api_definition_dirs, None)
        self.assertEqual(opts.original_proto_files, None)
        self.assertEqual(opts.update_proto_files, None)
        self.assertTrue(opts.use_descriptor_set())
        self.assertFalse(opts.use_proto_dirs())
        self.assertTrue(opts.human_readable_message)
        # Use default json path if not set.
        self.assertEqual(
            opts.output_json_path,
            os.path.join(os.getcwd(), "detected_breaking_changes.json"),
        )

    def test_options_directory_not_existing(self):
        with self.assertRaises(TypeError):
            # The directory is not existing, raise TypeError.
            Options(
                original_api_definition_dirs="c,d",
                update_api_definition_dirs="a,b",
                original_proto_files="pf1",
                update_proto_files="pf1",
                original_descriptor_set_file_path=None,
                update_descriptor_set_file_path=None,
            )

    def test_options_descriptor_set_not_existing(self):
        with self.assertRaises(TypeError):
            # The directory is not existing, raise TypeError.
            Options(
                original_api_definition_dirs=None,
                update_api_definition_dirs=None,
                original_proto_files=None,
                update_proto_files=None,
                original_descriptor_set_file_path="fake_descriptor_set.pb",
                update_descriptor_set_file_path="fake_descriptor_set.pb",
            )

    def test_options_invalid_args(self):
        with self.assertRaises(_InvalidArgumentsException):
            with mock.patch("os.path.isdir") as mocked_isdir:
                mocked_isdir.return_value = True
                with mock.patch("os.path.isfile") as mocked_isfile:
                    mocked_isfile.return_value = True
                    # Either directories of the proto definition files or
                    # path of the descriptor set file should be specified.
                    Options(
                        original_api_definition_dirs="a,b",
                        update_api_definition_dirs=None,
                        original_proto_files=None,
                        update_proto_files=None,
                        original_descriptor_set_file_path="fake_descriptor_set.pb",
                        update_descriptor_set_file_path=None,
                    )


if __name__ == "__main__":
    unittest.main()

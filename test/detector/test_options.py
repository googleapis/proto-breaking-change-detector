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
from src.detector.options import Options, _InvalidArgumentsException


class OptionsTest(unittest.TestCase):
    def test_options_proto_dirs_default(self):
        with mock.patch("os.path.isdir") as mocked_isdir:
            mocked_isdir.return_value = True
            opts = Options(
                original_api_definition_dirs="c,d",
                update_api_definition_dirs="a,b",
                original_descriptor_set_file_path=None,
                update_descriptor_set_file_path=None,
            )
        self.assertEqual(opts.original_api_definition_dirs, ["c", "d"])
        self.assertEqual(opts.update_api_definition_dirs, ["a", "b"])
        # Default value for human_readable_message is False.
        self.assertFalse(opts.human_readable_message)
        # Package_prefixes should be None if not set, no
        # external dependencie is needed.
        self.assertEqual(opts.package_prefixes, None)
        self.assertEqual(opts.original_descriptor_set_file_path, None)
        self.assertEqual(opts.update_descriptor_set_file_path, None)
        self.assertTrue(opts.use_proto_dirs())
        self.assertFalse(opts.use_descriptor_set())
        # Use default json path if not set.
        self.assertEqual(
            opts.output_json_path,
            os.path.join(os.getcwd(), "detected_breaking_changes.json"),
        )

    def test_options_proto_dirs(self):
        with mock.patch("os.path.isdir") as mocked_isdir:
            mocked_isdir.return_value = True
            opts = Options(
                original_api_definition_dirs="c,d",
                update_api_definition_dirs="a,b",
                original_descriptor_set_file_path=None,
                update_descriptor_set_file_path=None,
                human_readable_message=True,
                package_prefixes="prefix1, prefix2, prefix3",
            )
        self.assertEqual(opts.original_api_definition_dirs, ["c", "d"])
        self.assertEqual(opts.update_api_definition_dirs, ["a", "b"])
        self.assertTrue(opts.human_readable_message)
        # Strip the unneeded whitespaces.
        self.assertEqual(opts.package_prefixes, ["prefix1", "prefix2", "prefix3"])
        # Use default json path if not set.
        self.assertEqual(
            opts.output_json_path,
            os.path.join(os.getcwd(), "detected_breaking_changes.json"),
        )

    def test_options_descriptor_set_file(self):
        with mock.patch("os.path.isfile") as mocked_isfile:
            mocked_isfile.return_value = True
            opts = Options(
                original_api_definition_dirs=None,
                update_api_definition_dirs=None,
                original_descriptor_set_file_path="descriptor_set_original.pb",
                update_descriptor_set_file_path="descriptor_set_udpate.pb",
                human_readable_message=True,
                package_prefixes="prefix1, prefix2, prefix3",
            )
        self.assertEqual(
            opts.original_descriptor_set_file_path, "descriptor_set_original.pb"
        )
        self.assertEqual(
            opts.update_descriptor_set_file_path, "descriptor_set_udpate.pb"
        )
        self.assertEqual(opts.original_api_definition_dirs, None)
        self.assertEqual(opts.update_api_definition_dirs, None)
        self.assertTrue(opts.use_descriptor_set())
        self.assertFalse(opts.use_proto_dirs())
        self.assertTrue(opts.human_readable_message)
        # Strip the unneeded whitespaces.
        self.assertEqual(opts.package_prefixes, ["prefix1", "prefix2", "prefix3"])
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
                original_descriptor_set_file_path=None,
                update_descriptor_set_file_path=None,
            )

    def test_options_descriptor_set_not_existing(self):
        with self.assertRaises(TypeError):
            # The directory is not existing, raise TypeError.
            Options(
                original_api_definition_dirs=None,
                update_api_definition_dirs=None,
                original_descriptor_set_file_path="fake_descriptor_set.pb",
                update_descriptor_set_file_path="fake_descriptor_set.pb",
            )

    def test_options_json_file_not_existing(self):
        with self.assertRaises(TypeError):
            with mock.patch("os.path.isdir") as mocked_isdir:
                mocked_isdir.return_value = True
                # The output json file is not existing, raise TypeError.
                Options(
                    original_api_definition_dirs="c,d",
                    update_api_definition_dirs="a,b",
                    original_descriptor_set_file_path=None,
                    update_descriptor_set_file_path=None,
                    output_json_path="not_existing.json",
                )

    def test_options_invalid_args(self):
        with self.assertRaises(_InvalidArgumentsException):
            with mock.patch("os.path.isdir") as mocked_isdir:
                mocked_isdir.return_value = True
                with mock.patch("os.path.isfile") as mocked_isfile:
                    mocked_isfile.return_value = True
                    # Either dectories of the proto definintion files or
                    # path of the descriptor set file should be specified.
                    Options(
                        original_api_definition_dirs="a,b",
                        update_api_definition_dirs=None,
                        original_descriptor_set_file_path="fake_descriptor_set.pb",
                        update_descriptor_set_file_path=None,
                    )


if __name__ == "__main__":
    unittest.main()

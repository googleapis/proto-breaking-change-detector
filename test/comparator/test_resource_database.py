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
from google.api import resource_pb2
from src.comparator.resource_database import ResourceDatabase
from test.tools.mock_resources import make_resource_descriptor


class ResourceDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.resource_database = ResourceDatabase()

    def test_register_empty_resources(self):
        # Register resource is None, the database should be empty.
        self.resource_database.register_resource(None)
        self.assertFalse(self.resource_database.types)
        self.assertFalse(self.resource_database.patterns)

    def test_register_invalid_resource(self):
        # Register resource with no type.
        resource_without_type = make_resource_descriptor(
            resource_type=None, resource_patterns=["a"]
        )
        # Raise TypeError: APIs must define a resource type
        # and resource pattern for each resource in the API.
        with self.assertRaises(TypeError):
            self.resource_database.register_resource(resource_without_type)

    def test_register_valid_resource(self):
        resource = make_resource_descriptor(
            resource_type="resource", resource_patterns=["a"]
        )
        self.resource_database.register_resource(resource)
        self.assertEqual(list(self.resource_database.types.keys()), ["resource"])
        self.assertEqual(self.resource_database.types["resource"], resource)
        self.assertEqual(list(self.resource_database.patterns.keys()), ["a"])
        self.assertEqual(self.resource_database.patterns["a"], resource)

    def test_register_resource_with_multiple_patterns(self):
        resource = make_resource_descriptor(
            resource_type="resource", resource_patterns=["b", "c"]
        )
        self.resource_database.register_resource(resource)
        self.assertEqual(list(self.resource_database.types.keys()), ["resource"])
        self.assertEqual(self.resource_database.types["resource"], resource)
        self.assertEqual(list(self.resource_database.patterns.keys()), ["b", "c"])
        self.assertEqual(self.resource_database.patterns["b"], resource)
        self.assertEqual(self.resource_database.patterns["c"], resource)

    def test_get_resource_by_type(self):
        resource = make_resource_descriptor(
            resource_type="resource", resource_patterns=["a"]
        )
        self.resource_database.register_resource(resource)
        self.assertEqual(
            self.resource_database.get_resource_by_type("resource"), resource
        )
        self.assertEqual(self.resource_database.get_resource_by_type("resource1"), None)

    def test_get_resource_by_pattern(self):
        resource = make_resource_descriptor(
            resource_type="resource", resource_patterns=["a", "b"]
        )
        self.resource_database.register_resource(resource)
        # The resourc could be query by either type.
        self.assertEqual(self.resource_database.get_resource_by_pattern("a"), resource)
        self.assertEqual(self.resource_database.get_resource_by_pattern("b"), resource)

    def test_get_parent_resource_by_type(self):
        child_resource = make_resource_descriptor(
            resource_type="child", resource_patterns=["a/{a}/b/{b}", "b/{b}"]
        )
        parent_resource = make_resource_descriptor(
            resource_type="parent", resource_patterns=["a/{a}/b"]
        )
        self.resource_database.register_resource(child_resource)
        self.resource_database.register_resource(parent_resource)
        # `a/{a}/b` is the parent pattern of `a/{a}/b/{b}`
        parent_resources = self.resource_database.get_parent_resources_by_child_type(
            "child"
        )
        self.assertTrue(parent_resource in parent_resources)
        # Reverse query would not have any result.
        self.assertTrue(
            child_resource
            not in self.resource_database.get_parent_resources_by_child_type("parent")
        )


if __name__ == "__main__":
    unittest.main()

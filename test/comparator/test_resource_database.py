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
from google.api import resource_pb2
from test.tools.invoker import UnittestInvoker
from src.comparator.resource_database import ResourceDatabase
from src.comparator.wrappers import WithLocation


class ResourceDatabaseTest(unittest.TestCase):
    _INVOKER = UnittestInvoker(
        ["resource_database_v1.proto"], "resource_database_v1_descriptor_set.pb", True
    )

    def setUp(self):
        self.descriptor_set = self._INVOKER.run()
        self.resource_database = ResourceDatabase()

    def test_resource_database(self):
        for f in self.descriptor_set.file:
            resources = f.options.Extensions[resource_pb2.resource_definition]
            for resource in resources:
                resource_with_location = self._mock_resource(resource)
                self.resource_database.register_resource(resource_with_location)
                self.assertEqual(
                    self.resource_database.get_resource_by_type(resource.type),
                    resource_with_location,
                )
                self.assertEqual(
                    self.resource_database.get_resource_by_pattern(resource.pattern[0]),
                    resource_with_location,
                )
            # Check a non-existing resource, should return None.
            self.assertEqual(
                self.resource_database.get_resource_by_pattern("a/{a}/b{b}"),
                None,
            )
        # We should get the parent resource correctly by child_type.
        # The resource with pattern `foo/{foo}/bar/{bar}/t2` has the parent pattern of `foo/{foo}`
        # which is also defined in the proto by type `example.googleapis.com/t1`.
        parent_resource = self.resource_database.get_parent_resources_by_child_type(
            "example.googleapis.com/t2"
        )
        self.assertEqual(parent_resource[0].value.type, "example.googleapis.com/t1")

    def _mock_resource(self, resource):
        return WithLocation(
            resource, source_code_locations={}, path=(), proto_file_name=""
        )

    @classmethod
    def tearDownClass(cls):
        cls._INVOKER.cleanup()


if __name__ == "__main__":
    unittest.main()

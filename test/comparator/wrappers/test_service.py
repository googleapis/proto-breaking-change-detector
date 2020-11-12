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
from test.tools.mock_descriptors import (
    make_method,
    make_message,
    make_field,
    make_service,
)
from google.protobuf import descriptor_pb2


class ServiceTest(unittest.TestCase):
    def test_service_properties(self):
        service = make_service(name="ThingDoer")
        self.assertEqual(service.name, "ThingDoer")
        self.assertEqual(service.proto_file_name, "foo")
        self.assertEqual(service.path, ())
        self.assertEqual(
            service.source_code_line,
            "No source code line can be identified by path ().",
        )

    def test_service_host(self):
        service = make_service(host="thingdoer.googleapis.com")
        self.assertEqual(service.host, "thingdoer.googleapis.com")

    def test_service_no_host(self):
        service = make_service()
        self.assertEqual(service.host, "")

    def test_service_scopes(self):
        service = make_service(scopes=("https://foo/user/", "https://foo/admin/"))
        self.assertTrue("https://foo/user/" in service.oauth_scopes)
        self.assertTrue("https://foo/admin/" in service.oauth_scopes)

    def test_service_no_scopes(self):
        service = make_service()
        self.assertEqual(len(service.oauth_scopes), 0)

    def test_service_methods(self):
        input_message = make_message("InputRequest")
        output_message = make_message("OutputResponse")
        service = make_service(
            name="ThingDoer",
            methods=(
                make_method(
                    name="DoThing",
                    input_message=input_message,
                    output_message=output_message,
                ),
                make_method(
                    name="Jump",
                    input_message=input_message,
                    output_message=output_message,
                ),
                make_method(
                    name="Yawn",
                    input_message=input_message,
                    output_message=output_message,
                ),
            ),
        )
        expected_names = ["DoThing", "Jump", "Yawn"]
        self.assertEqual(list(service.methods.keys()), expected_names)

    def test_source_code_line(self):
        L = descriptor_pb2.SourceCodeInfo.Location
        locations = [
            L(path=(4, 0, 2, 1), span=(1, 2, 3, 4)),
        ]
        service = make_service(
            proto_file_name="test.proto",
            locations=locations,
            path=(4, 0, 2, 1),
        )
        self.assertEqual(service.source_code_line, 2)
        self.assertEqual(service.proto_file_name, "test.proto")


if __name__ == "__main__":
    unittest.main()

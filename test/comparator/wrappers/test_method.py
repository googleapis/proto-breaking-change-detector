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
from test.tools.mock_descriptors import make_method, make_message, make_field


class MethodTest(unittest.TestCase):
    def test_basic_properties(self):
        method = make_method("Foo")
        self.assertEqual(method.name, "Foo")
        self.assertEqual(method.proto_file_name, "foo")
        self.assertEqual(method.path, ())
        self.assertEqual(
            method.source_code_line,
            -1,
        )

    def test_method_types(self):
        input_msg = make_message(name="Input", full_name=".example.v1.input")
        output_msg = make_message(name="Output", full_name=".example.v1.output")
        method = make_method("DoSomething", input_msg, output_msg)
        self.assertEqual(method.name, "DoSomething")
        self.assertEqual(method.input.value, ".example.v1.input")
        self.assertEqual(method.output.value, ".example.v1.output")

    def test_method_streaming(self):
        method = make_method("F", client_streaming=True, server_streaming=True)
        self.assertEqual(method.client_streaming.value, True)
        self.assertEqual(method.server_streaming.value, True)

    def test_method_longrunning(self):
        input_msg = make_message(name="Input", full_name=".example.v1.input")
        output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method = make_method("DoSomething", input_msg, output_msg)
        self.assertEqual(method.name, "DoSomething")
        self.assertEqual(method.input.value, ".example.v1.input")
        self.assertEqual(method.output.value, ".google.longrunning.Operation")
        self.assertEqual(method.longrunning, True)

    def test_method_paged(self):
        field_next_page_token = make_field(
            name="next_page_token",
            proto_type="TYPE_STRING",
            number=2,
        )
        field_repeated = make_field(
            name="repeated_field",
            proto_type="TYPE_STRING",
            repeated=True,
            number=1,
        )
        response_message = make_message(
            name="ResponseMessage",
            fields=[field_repeated, field_next_page_token],
            full_name=".example.v1.ResponseMessage",
        )
        field_page_size = make_field(
            name="page_size",
            proto_type="TYPE_INT32",
            number=1,
        )
        field_page_token = make_field(
            name="page_token",
            proto_type="TYPE_STRING",
            number=2,
        )
        request_message = make_message(
            name="RequestMessage",
            fields=[field_page_size, field_page_token],
            full_name=".example.v1.RequestMessage",
        )
        messages_map = {
            ".example.v1.ResponseMessage": response_message,
            ".example.v1.RequestMessage": request_message,
        }
        method = make_method(
            name="PagedMethod",
            input_message=request_message,
            output_message=response_message,
            messages_map=messages_map,
        )
        self.assertEqual(method.paged_result_field.name, "repeated_field")
        self.assertEqual(method.longrunning, False)

    def test_method_no_page_field(self):
        # No repeated field in the response message.
        field_next_page_token = make_field(
            name="next_page_token",
            proto_type="TYPE_STRING",
            number=2,
        )
        response_message = make_message(
            name="ResponseMessage",
            fields=[field_next_page_token],
        )
        field_page_size = make_field(
            name="page_size",
            proto_type="TYPE_INT32",
            number=1,
        )
        field_page_token = make_field(
            name="page_token",
            proto_type="TYPE_STRING",
            number=2,
        )
        request_message = make_message(
            name="RequestMessage",
            fields=[field_page_size, field_page_token],
        )
        messages_map = {
            "ResponseMessage": response_message,
            "RequestMessage": request_message,
        }
        method = make_method(
            name="PagedMethod",
            input_message=request_message,
            output_message=response_message,
            messages_map=messages_map,
        )
        self.assertEqual(method.paged_result_field, None)
        # Missing `page_size` in request message.
        request_message_without_page_size = make_message(
            name="RequestMessage",
            fields=[field_page_size],
        )
        method = make_method(
            name="NoPagedMethod",
            input_message=request_message_without_page_size,
            output_message=response_message,
            messages_map=messages_map,
        )
        self.assertEqual(method.paged_result_field, None)
        # Missing `next_page_token` in response message.
        response_message_without_next_page_token = make_message(
            name="ResponseMessage",
        )
        method = make_method(
            name="NoPagedMethod",
            input_message=request_message,
            output_message=response_message_without_next_page_token,
            messages_map=messages_map,
        )
        self.assertEqual(method.paged_result_field, None)

    def test_method_signatures(self):
        method = make_method("Method", signatures=["sig1", "sig2"])
        self.assertEqual(method.method_signatures.value, [("sig1",), ("sig2",)])

    def test_method_lro_annotationn(self):
        input_msg = make_message(name="Input", full_name=".example.v1.input")
        output_msg = make_message(
            name=".google.longrunning.Operation",
            full_name=".google.longrunning.Operation",
        )
        method = make_method(
            name="Method",
            input_message=input_msg,
            output_message=output_msg,
            lro_response_type="response_type",
            lro_metadata_type="metadata_type",
        )
        lro_annotation = method.lro_annotation.value
        self.assertEqual(lro_annotation["response_type"], "response_type")
        self.assertEqual(lro_annotation["metadata_type"], "metadata_type")

    def test_method_http_annotationn(self):
        method = make_method(
            name="Method",
            http_uri="http_uri",
            http_body="*",
        )
        http_annotation = method.http_annotation.value
        self.assertEqual(http_annotation["http_method"], "get")
        self.assertEqual(http_annotation["http_uri"], "http_uri")
        self.assertEqual(http_annotation["http_body"], "*")


if __name__ == "__main__":
    unittest.main()

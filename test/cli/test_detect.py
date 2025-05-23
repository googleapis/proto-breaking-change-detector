# Copyright 2021 Google LLC
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
# See the License of the specific language governing permissions and
# limitations under the License.

import unittest
import os
import tempfile
import json
from click.testing import CliRunner
from proto_bcd.cli.detect import detect
from unittest.mock import patch
from io import StringIO


class CliDetectTest(unittest.TestCase):
    maxDiff = None
    COMMON_PROTOS_DIR = os.path.join(os.getcwd(), "api-common-protos")
    COMMON_RESOURCE = os.path.join(
        os.getcwd(), "googleapis/google/cloud/common_resources.proto"
    )
    GOOGLEAPI_DIR = os.path.join(os.getcwd(), "googleapis/")

    def test_descriptor_set_enum(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_descriptor_set_file_path=test/testdata/protos/enum/v1/enum_descriptor_set.pb",
                    "--update_descriptor_set_file_path=test/testdata/protos/enum/v1beta1/enum_descriptor_set.pb",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: remove enum `BookType`.\n",
            )

    def test_single_directory_enum(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--update_proto_files=test/testdata/protos/enum/v1beta1/enum_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: remove enum `BookType`.\n",
            )

    def test_single_directory_enum_completely_removed(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: remove enum `BookType`.\n",
            )

    def test_single_directory_enum_without_updated_protos(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: remove enum `BookType`.\n",
            )

    def test_single_directory_enum_empty_updated_protos_list(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--update_proto_files=",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "enum_v1.proto L5: remove enum `BookType`.\n",
            )

    def test_single_directory_service_empty(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/service/v1",
                    "--original_proto_files=test/testdata/protos/service/v1/service_v1.proto",
                    "--update_api_definition_dirs=",
                    "--update_proto_files=",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "service_v1.proto L6: remove service `Example`.\n"
                + "service_v1.proto L18: remove message `FooRequest`.\n"
                + "service_v1.proto L20: remove message `FooResponse`.\n"
                + "service_v1.proto L22: remove message `BarRequest`.\n"
                + "service_v1.proto L27: remove message `BarResponse`.\n",
            )

    def test_single_directory_change_to_optional(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/optional/original",
                    "--update_api_definition_dirs=test/testdata/protos/optional/updated",
                    "--original_proto_files=test/testdata/protos/optional/original/optional.proto",
                    "--update_proto_files=test/testdata/protos/optional/updated/optional.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "optional.proto L6: change proto3 optional flag of field `.example.v1.Test.enabled`.\n",
            )

    def test_single_directory_enum_alias(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta2",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--update_proto_files=test/testdata/protos/enum/v1beta2/enum_v1beta2.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            # No major findings
            self.assertEqual(result.output, "")

    def test_single_directory_enum_json(self):
        # Mock the stdout so that the unit test does not
        # print anything to the console.
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        tmpfile.close()
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/enum/v1",
                    "--update_api_definition_dirs=test/testdata/protos/enum/v1beta1",
                    "--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto",
                    "--update_proto_files=test/testdata/protos/enum/v1beta1/enum_v1beta1.proto",
                    "--output_json_path=" + tmpfile.name,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(tmpfile.name, "r") as json_file:
                json_obj = json.load(json_file)
                self.assertEqual(len(json_obj), 2)
            os.unlink(tmpfile.name)

    def test_single_directory_message(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/message/v1",
                    "--update_api_definition_dirs=test/testdata/protos/message/v1beta1",
                    "--original_proto_files=test/testdata/protos/message/v1/message_v1.proto",
                    "--update_proto_files=test/testdata/protos/message/v1beta1/message_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "message_v1.proto L6: move message `Person` from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1.proto L24: move message `PhoneNumber` from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1.proto L26: remove field `.tutorial.v1.Person.type`.\n"
                + "message_v1.proto L37: move message `AddressBook` from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1beta1.proto L12: change type of field `.tutorial.v1.Person.id` from `int32` to `string`.\n"
                + "message_v1beta1.proto L14: rename field `.tutorial.v1.Person.email` to `.tutorial.v1.Person.email_address`.\n"
                + "message_v1beta1.proto L29: change repeated flag of field `.tutorial.v1.Person.phones`.\n"
                + "message_v1beta1.proto L30: move field `.tutorial.v1.Person.single` out of oneof.\n",
            )

    def test_single_directory_message_all_changes(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/message/v1",
                    "--update_api_definition_dirs=test/testdata/protos/message/v1beta1",
                    "--original_proto_files=test/testdata/protos/message/v1/message_v1.proto",
                    "--update_proto_files=test/testdata/protos/message/v1beta1/message_v1beta1.proto",
                    "--human_readable_message",
                    "--all_changes",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "message_v1.proto L6: move message `Person` from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1.proto L24: move message `PhoneNumber` from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1.proto L26: remove field `.tutorial.v1.Person.type`.\n"
                + "message_v1.proto L37: move message `AddressBook` from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1beta1.proto L6: change comment of message `Person`.\n"
                + "message_v1beta1.proto L8: change comment of field `.tutorial.v1.Person.name`.\n"
                + "message_v1beta1.proto L12: change comment of field `.tutorial.v1.Person.id`.\n"
                + "message_v1beta1.proto L12: change type of field `.tutorial.v1.Person.id` from `int32` to `string`.\n"
                + "message_v1beta1.proto L14: rename field `.tutorial.v1.Person.email` to `.tutorial.v1.Person.email_address`.\n"
                + "message_v1beta1.proto L17: change comment of enum `PhoneType`.\n"
                + "message_v1beta1.proto L19: change comment of enum value `PhoneType.MOBILE`.\n"
                + "message_v1beta1.proto L22: add enum value `PhoneType.SCHOOL`.\n"
                + "message_v1beta1.proto L29: change repeated flag of field `.tutorial.v1.Person.phones`.\n"
                + "message_v1beta1.proto L30: move field `.tutorial.v1.Person.single` out of oneof.\n",
            )

    def test_single_directory_service(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/service/v1",
                    "--update_api_definition_dirs=test/testdata/protos/service/v1beta1",
                    "--original_proto_files=test/testdata/protos/service/v1/service_v1.proto",
                    "--update_proto_files=test/testdata/protos/service/v1beta1/service_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "service_v1.proto L13: remove rpc method `Example.ShouldRemove`.\n"
                + "service_v1.proto L18: move message `FooRequest` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L20: move message `FooResponse` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L22: move message `BarRequest` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L23: remove field `.example.v1.BarRequest.page_size`.\n"
                + "service_v1.proto L24: remove field `.example.v1.BarRequest.page_token`.\n"
                + "service_v1.proto L27: move message `BarResponse` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L28: remove field `.example.v1.BarResponse.content`.\n"
                + "service_v1.proto L29: remove field `.example.v1.BarResponse.next_page_token`.\n"
                + "service_v1beta1.proto L9: change input type of rpc method `Example.Foo` from `.example.v1.FooRequest` to `.example.v1beta1.FooRequestUpdate`.\n"
                + "service_v1beta1.proto L9: change response type of rpc method `Example.Foo` from `.example.v1.FooResponse` to `.example.v1beta1.FooResponseUpdate`.\n"
                + "service_v1beta1.proto L11: change client streaming flag of rpc method `Example.Bar`.\n"
                + "service_v1beta1.proto L11: change server streaming flag of rpc method `Example.Bar`.\n"
                + "service_v1beta1.proto L13: change pagination feature of rpc method `Example.PaginatedMethod`.\n",
            )

    def test_single_directory_service_all_changes(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/service/v1",
                    "--update_api_definition_dirs=test/testdata/protos/service/v1beta1",
                    "--original_proto_files=test/testdata/protos/service/v1/service_v1.proto",
                    "--update_proto_files=test/testdata/protos/service/v1beta1/service_v1beta1.proto",
                    "--human_readable_message",
                    "--all_changes",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "service_v1.proto L13: remove rpc method `Example.ShouldRemove`.\n"
                + "service_v1.proto L18: move message `FooRequest` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L20: move message `FooResponse` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L22: move message `BarRequest` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L23: remove field `.example.v1.BarRequest.page_size`.\n"
                + "service_v1.proto L24: remove field `.example.v1.BarRequest.page_token`.\n"
                + "service_v1.proto L27: move message `BarResponse` from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L28: remove field `.example.v1.BarResponse.content`.\n"
                + "service_v1.proto L29: remove field `.example.v1.BarResponse.next_page_token`.\n"
                + "service_v1beta1.proto L6: change comment of service `Example`.\n"
                + "service_v1beta1.proto L9: change comment of rpc method `Example.Foo`.\n"
                + "service_v1beta1.proto L9: change input type of rpc method `Example.Foo` from `.example.v1.FooRequest` to `.example.v1beta1.FooRequestUpdate`.\n"
                + "service_v1beta1.proto L9: change response type of rpc method `Example.Foo` from `.example.v1.FooResponse` to `.example.v1beta1.FooResponseUpdate`.\n"
                + "service_v1beta1.proto L11: change client streaming flag of rpc method `Example.Bar`.\n"
                + "service_v1beta1.proto L11: change server streaming flag of rpc method `Example.Bar`.\n"
                + "service_v1beta1.proto L13: change pagination feature of rpc method `Example.PaginatedMethod`.\n"
                + "service_v1beta1.proto L20: add message `FooRequestUpdate`.\n"
                + "service_v1beta1.proto L22: add message `FooResponseUpdate`.\n",
            )

    def test_single_directory_service_annotation(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=test/testdata/protos/service_annotation/v1,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=test/testdata/protos/service_annotation/v1beta1,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=test/testdata/protos/service_annotation/v1/service_annotation_v1.proto",
                    "--update_proto_files=test/testdata/protos/service_annotation/v1beta1/service_annotation_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "service_annotation_v1.proto L18: remove method_signature `content,error` from rpc method `Example.Foo`.\n"
                + "service_annotation_v1.proto L33: move message `FooRequest` from `service_annotation_v1.proto` to `service_annotation_v1beta1.proto`.\n"
                + "service_annotation_v1.proto L38: move message `FooResponse` from `service_annotation_v1.proto` to `service_annotation_v1beta1.proto`.\n"
                + "service_annotation_v1.proto L40: remove message `FooMetadata`.\n"
                + "service_annotation_v1beta1.proto L14: change google.api.http annotation `http_method` of rpc method `Example.Foo`.\n"
                + "service_annotation_v1beta1.proto L22: change google.api.http annotation `http_body` of rpc method `Example.Bar`.\n"
                + "service_annotation_v1beta1.proto L26: change long running operation metadata type of rpc method `Example.Bar` from `FooMetadata` to `FooMetadataUpdate`.\n",
            )

    def test_single_directory_method_signature_order(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=test/testdata/protos/method_signature_order/v1,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=test/testdata/protos/method_signature_order/v1beta1,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=test/testdata/protos/method_signature_order/v1/signature_order_v1.proto",
                    "--update_proto_files=test/testdata/protos/method_signature_order/v1beta1/signature_order_v1beta1.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "signature_order_v1.proto L16: change position of method_signature `id,content` of rpc method `Example.Foo`.\n"
                + "signature_order_v1.proto L16: change position of method_signature `id,uri` of rpc method `Example.Foo`.\n"
                + "signature_order_v1.proto L21: move message `FooRequest` from `signature_order_v1.proto` to `signature_order_v1beta1.proto`.\n"
                + "signature_order_v1.proto L29: move message `FooResponse` from `signature_order_v1.proto` to `signature_order_v1beta1.proto`.\n",
            )

    def test_oslogin_proto_alpha(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/cloud/oslogin/v1/oslogin.proto",
                    "--update_proto_files=googleapis/google/cloud/oslogin/v1alpha/oslogin.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/cloud/oslogin/v1/oslogin.proto L34: remove packaging option `Google::Cloud::OsLogin::V1` from `ruby_package`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L41: remove default host `oslogin.googleapis.com` from service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L42: remove oauth_scope `https://www.googleapis.com/auth/cloud-platform` from service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L42: remove oauth_scope `https://www.googleapis.com/auth/compute` from service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L51: remove method_signature `name` from rpc method `OsLoginService.DeletePosixAccount`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L59: remove method_signature `name` from rpc method `OsLoginService.DeleteSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L68: remove method_signature `name` from rpc method `OsLoginService.GetLoginProfile`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L76: remove method_signature `name` from rpc method `OsLoginService.GetSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L87: remove method_signature `parent,ssh_public_key` from rpc method `OsLoginService.ImportSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L87: remove method_signature `parent,ssh_public_key,project_id` from rpc method `OsLoginService.ImportSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L98: remove method_signature `name,ssh_public_key` from rpc method `OsLoginService.UpdateSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L98: remove method_signature `name,ssh_public_key,update_mask` from rpc method `OsLoginService.UpdateSshPublicKey`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L123: remove resource_reference option from field `.google.cloud.oslogin.v1.DeletePosixAccountRequest.name`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L136: remove resource_reference option from field `.google.cloud.oslogin.v1.DeleteSshPublicKeyRequest.name`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L147: remove resource_reference option from field `.google.cloud.oslogin.v1.GetLoginProfileRequest.name`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L153: remove field `.google.cloud.oslogin.v1.GetLoginProfileRequest.project_id`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L156: remove field `.google.cloud.oslogin.v1.GetLoginProfileRequest.system_id`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L166: remove resource_reference option from field `.google.cloud.oslogin.v1.GetSshPublicKeyRequest.name`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L177: remove resource_reference option from field `.google.cloud.oslogin.v1.ImportSshPublicKeyRequest.parent`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L202: remove resource_reference option from field `.google.cloud.oslogin.v1.UpdateSshPublicKeyRequest.name`.\n",
            )

    def test_oslogin_proto_beta(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/cloud/oslogin/v1/oslogin.proto",
                    "--update_proto_files=googleapis/google/cloud/oslogin/v1beta/oslogin.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/cloud/oslogin/v1beta/oslogin.proto L179: change field behavior of field `.google.cloud.oslogin.v1.ImportSshPublicKeyRequest.ssh_public_key`.\n",
            )

    def test_pubsub_proto(self):
        pubsub_v1beta2 = os.path.join(
            self.GOOGLEAPI_DIR, "google/pubsub/v1beta2/pubsub.proto"
        )
        pubsub_v1 = os.path.join(self.GOOGLEAPI_DIR, "google/pubsub/v1/pubsub.proto")
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs={self.GOOGLEAPI_DIR},{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs={self.GOOGLEAPI_DIR},{self.COMMON_PROTOS_DIR}",
                    f"--original_proto_files={pubsub_v1beta2},{self.COMMON_RESOURCE}",
                    f"--update_proto_files={pubsub_v1},{self.COMMON_RESOURCE}",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/pubsub/v1/pubsub.proto L160: change field behavior of field `.google.pubsub.v1beta2.Topic.name`.\n"
                + "google/pubsub/v1/pubsub.proto L221: change field behavior of field `.google.pubsub.v1beta2.GetTopicRequest.topic`.\n"
                + "google/pubsub/v1/pubsub.proto L245: change field behavior of field `.google.pubsub.v1beta2.PublishRequest.topic`.\n"
                + "google/pubsub/v1/pubsub.proto L250: change field behavior of field `.google.pubsub.v1beta2.PublishRequest.messages`.\n"
                + "google/pubsub/v1/pubsub.proto L266: change field behavior of field `.google.pubsub.v1beta2.ListTopicsRequest.project`.\n"
                + "google/pubsub/v1/pubsub.proto L296: change field behavior of field `.google.pubsub.v1beta2.ListTopicSubscriptionsRequest.topic`.\n"
                + "google/pubsub/v1/pubsub.proto L356: change field behavior of field `.google.pubsub.v1beta2.DeleteTopicRequest.topic`.\n"
                + "google/pubsub/v1/pubsub.proto L617: change field behavior of field `.google.pubsub.v1beta2.Subscription.name`.\n"
                + "google/pubsub/v1/pubsub.proto L623: change field behavior of field `.google.pubsub.v1beta2.Subscription.topic`.\n"
                + "google/pubsub/v1/pubsub.proto L880: change field behavior of field `.google.pubsub.v1beta2.GetSubscriptionRequest.subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L903: change field behavior of field `.google.pubsub.v1beta2.ListSubscriptionsRequest.project`.\n"
                + "google/pubsub/v1/pubsub.proto L934: change field behavior of field `.google.pubsub.v1beta2.DeleteSubscriptionRequest.subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L946: change field behavior of field `.google.pubsub.v1beta2.ModifyPushConfigRequest.subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L958: change field behavior of field `.google.pubsub.v1beta2.ModifyPushConfigRequest.push_config`.\n"
                + "google/pubsub/v1/pubsub.proto L966: change field behavior of field `.google.pubsub.v1beta2.PullRequest.subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L985: change field behavior of field `.google.pubsub.v1beta2.PullRequest.max_messages`.\n"
                + "google/pubsub/v1/pubsub.proto L1002: change field behavior of field `.google.pubsub.v1beta2.ModifyAckDeadlineRequest.subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L1009: add REQUIRED field `.google.pubsub.v1beta2.ModifyAckDeadlineRequest.ack_ids`.\n"
                + "google/pubsub/v1/pubsub.proto L1019: change field behavior of field `.google.pubsub.v1beta2.ModifyAckDeadlineRequest.ack_deadline_seconds`.\n"
                + "google/pubsub/v1/pubsub.proto L1027: change field behavior of field `.google.pubsub.v1beta2.AcknowledgeRequest.subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L1036: change field behavior of field `.google.pubsub.v1beta2.AcknowledgeRequest.ack_ids`.\n"
                + "google/pubsub/v1beta2/pubsub.proto L369: remove field `.google.pubsub.v1beta2.ModifyAckDeadlineRequest.ack_id`.\n",
            )

    def test_tts_proto(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/cloud/texttospeech/v1beta1/cloud_tts.proto",
                    "--update_proto_files=googleapis/google/cloud/texttospeech/v1/cloud_tts.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/cloud/texttospeech/v1beta1/cloud_tts.proto L103: remove enum value `AudioEncoding.MP3_64_KBPS`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L113: remove enum value `AudioEncoding.MULAW`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L142: remove enum `TimepointType`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L160: remove field `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechRequest.enable_time_pointing`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L275: remove field `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse.timepoints`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L278: remove field `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse.audio_config`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L283: remove message `Timepoint`.\n",
            )

    def test_tts_proto_no_line_numbers(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    f"--original_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    f"--update_api_definition_dirs=googleapis/,{self.COMMON_PROTOS_DIR}",
                    "--original_proto_files=googleapis/google/cloud/texttospeech/v1beta1/cloud_tts.proto",
                    "--update_proto_files=googleapis/google/cloud/texttospeech/v1/cloud_tts.proto",
                    "--human_readable_message",
                    "--no_line_numbers",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove enum value `AudioEncoding.MP3_64_KBPS`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove enum value `AudioEncoding.MULAW`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove enum `TimepointType`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove field `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechRequest.enable_time_pointing`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove field `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse.timepoints`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove field `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse.audio_config`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: remove message `Timepoint`.\n",
            )

    def test_nonbreaking_changes_not_reported(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/nonbreaking/old",
                    "--update_api_definition_dirs=test/testdata/protos/nonbreaking/new",
                    "--original_proto_files=test/testdata/protos/nonbreaking/old/file.proto",
                    "--update_proto_files=test/testdata/protos/nonbreaking/new/file.proto",
                    "--human_readable_message",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, "")

    def test_nonbreaking_changes_reported_if_requested(self):
        with patch("sys.stdout", new=StringIO()):
            runner = CliRunner()
            result = runner.invoke(
                detect,
                [
                    "--original_api_definition_dirs=test/testdata/protos/nonbreaking/old",
                    "--update_api_definition_dirs=test/testdata/protos/nonbreaking/new",
                    "--original_proto_files=test/testdata/protos/nonbreaking/old/file.proto",
                    "--update_proto_files=test/testdata/protos/nonbreaking/new/file.proto",
                    "--human_readable_message",
                    "--all_changes",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "file.proto L7: add field `.test_non_breaking.Message.added`.\n",
            )


if __name__ == "__main__":
    unittest.main()

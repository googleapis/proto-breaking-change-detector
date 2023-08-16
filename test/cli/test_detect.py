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
# See the License for the specific language governing permissions and
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
                "enum_v1.proto L5: An existing enum `BookType` is removed.\n",
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
                "enum_v1.proto L5: An existing enum `BookType` is removed.\n",
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
                "optional.proto L6: Changed proto3 optional flag of an existing field `enabled` in message `.example.v1.Test`.\n",
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
                "message_v1.proto L5: An existing message `Person` is moved from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1.proto L16: An existing message `PhoneNumber` is moved from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1.proto L18: An existing field `type` is removed from message `.tutorial.v1.Person`.\n"
                + "message_v1.proto L27: An existing message `AddressBook` is moved from `message_v1.proto` to `message_v1beta1.proto`.\n"
                + "message_v1beta1.proto L7: The type of an existing field `id` is changed from `int32` to `string` in message `.tutorial.v1.Person`.\n"
                + "message_v1beta1.proto L8: An existing field `email` is renamed to `email_address` in message `.tutorial.v1.Person`.\n"
                + "message_v1beta1.proto L21: Changed repeated flag of an existing field `phones` in message `.tutorial.v1.Person`.\n"
                + "message_v1beta1.proto L22: An existing field `single` is moved out of oneof in message `.tutorial.v1.Person`.\n",
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
                "service_v1.proto L11: An existing method `ShouldRemove` is removed from service `Example`.\n"
                + "service_v1.proto L16: An existing message `FooRequest` is moved from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L18: An existing message `FooResponse` is moved from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L20: An existing message `BarRequest` is moved from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L21: An existing field `page_size` is removed from message `.example.v1.BarRequest`.\n"
                + "service_v1.proto L22: An existing field `page_token` is removed from message `.example.v1.BarRequest`.\n"
                + "service_v1.proto L25: An existing message `BarResponse` is moved from `service_v1.proto` to `service_v1beta1.proto`.\n"
                + "service_v1.proto L26: An existing field `content` is removed from message `.example.v1.BarResponse`.\n"
                + "service_v1.proto L27: An existing field `next_page_token` is removed from message `.example.v1.BarResponse`.\n"
                + "service_v1beta1.proto L7: Input type of method `Foo` is changed from `.example.v1.FooRequest` to `.example.v1beta1.FooRequestUpdate` in service `Example`.\n"
                + "service_v1beta1.proto L7: Response type of method `Foo` is changed from `.example.v1.FooResponse` to `.example.v1beta1.FooResponseUpdate` in service `Example`.\n"
                + "service_v1beta1.proto L9: Client streaming flag is changed for method `Bar` in service `Example`.\n"
                + "service_v1beta1.proto L9: Server streaming flag is changed for method `Bar` in service `Example`.\n"
                + "service_v1beta1.proto L11: Pagination feature is changed for method `PaginatedMethod` in service `Example`.\n",
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
                "service_annotation_v1.proto L18: An existing method_signature `content,error` is removed from method `Foo` in service `Example`.\n"
                + "service_annotation_v1.proto L33: An existing message `FooRequest` is moved from `service_annotation_v1.proto` to `service_annotation_v1beta1.proto`.\n"
                + "service_annotation_v1.proto L38: An existing message `FooResponse` is moved from `service_annotation_v1.proto` to `service_annotation_v1beta1.proto`.\n"
                + "service_annotation_v1.proto L40: An existing message `FooMetadata` is removed.\n"
                + "service_annotation_v1beta1.proto L14: An existing google.api.http annotation `http_method` is changed for method `Foo` in service `Example`.\n"
                + "service_annotation_v1beta1.proto L22: An existing google.api.http annotation `http_body` is changed for method `Bar` in service `Example`.\n"
                + "service_annotation_v1beta1.proto L26: Long running operation metadata type is changed from `FooMetadata` to `FooMetadataUpdate` for method `Bar` in service `Example`.\n",
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
                "signature_order_v1.proto L16: An existing method_signature `id,content` has changed its position in method `Foo` in service `Example`.\n"
                + "signature_order_v1.proto L16: An existing method_signature `id,uri` has changed its position in method `Foo` in service `Example`.\n"
                + "signature_order_v1.proto L21: An existing message `FooRequest` is moved from `signature_order_v1.proto` to `signature_order_v1beta1.proto`.\n"
                + "signature_order_v1.proto L29: An existing message `FooResponse` is moved from `signature_order_v1.proto` to `signature_order_v1beta1.proto`.\n",
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
                "google/cloud/oslogin/v1/oslogin.proto L34: An existing packaging option `Google::Cloud::OsLogin::V1` for `ruby_package` is removed.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L41: An existing default host `oslogin.googleapis.com` is removed from service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L42: An existing oauth_scope `https://www.googleapis.com/auth/cloud-platform` is removed from service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L42: An existing oauth_scope `https://www.googleapis.com/auth/compute` is removed from service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L51: An existing method_signature `name` is removed from method `DeletePosixAccount` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L59: An existing method_signature `name` is removed from method `DeleteSshPublicKey` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L68: An existing method_signature `name` is removed from method `GetLoginProfile` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L76: An existing method_signature `name` is removed from method `GetSshPublicKey` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L87: An existing method_signature `parent,ssh_public_key` is removed from method `ImportSshPublicKey` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L87: An existing method_signature `parent,ssh_public_key,project_id` is removed from method `ImportSshPublicKey` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L98: An existing method_signature `name,ssh_public_key` is removed from method `UpdateSshPublicKey` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L98: An existing method_signature `name,ssh_public_key,update_mask` is removed from method `UpdateSshPublicKey` in service `OsLoginService`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L123: An existing resource_reference option of the field `name` is removed in message `.google.cloud.oslogin.v1.DeletePosixAccountRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L136: An existing resource_reference option of the field `name` is removed in message `.google.cloud.oslogin.v1.DeleteSshPublicKeyRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L147: An existing resource_reference option of the field `name` is removed in message `.google.cloud.oslogin.v1.GetLoginProfileRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L153: An existing field `project_id` is removed from message `.google.cloud.oslogin.v1.GetLoginProfileRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L156: An existing field `system_id` is removed from message `.google.cloud.oslogin.v1.GetLoginProfileRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L166: An existing resource_reference option of the field `name` is removed in message `.google.cloud.oslogin.v1.GetSshPublicKeyRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L177: An existing resource_reference option of the field `parent` is removed in message `.google.cloud.oslogin.v1.ImportSshPublicKeyRequest`.\n"
                + "google/cloud/oslogin/v1/oslogin.proto L202: An existing resource_reference option of the field `name` is removed in message `.google.cloud.oslogin.v1.UpdateSshPublicKeyRequest`.\n",
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
                "google/cloud/oslogin/v1beta/oslogin.proto L179: Changed field behavior for an existing field `ssh_public_key` in message `.google.cloud.oslogin.v1.ImportSshPublicKeyRequest`.\n",
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
                "google/pubsub/v1/pubsub.proto L160: Changed field behavior for an existing field `name` in message `.google.pubsub.v1beta2.Topic`.\n"
                + "google/pubsub/v1/pubsub.proto L221: Changed field behavior for an existing field `topic` in message `.google.pubsub.v1beta2.GetTopicRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L245: Changed field behavior for an existing field `topic` in message `.google.pubsub.v1beta2.PublishRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L250: Changed field behavior for an existing field `messages` in message `.google.pubsub.v1beta2.PublishRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L266: Changed field behavior for an existing field `project` in message `.google.pubsub.v1beta2.ListTopicsRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L296: Changed field behavior for an existing field `topic` in message `.google.pubsub.v1beta2.ListTopicSubscriptionsRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L356: Changed field behavior for an existing field `topic` in message `.google.pubsub.v1beta2.DeleteTopicRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L617: Changed field behavior for an existing field `name` in message `.google.pubsub.v1beta2.Subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L623: Changed field behavior for an existing field `topic` in message `.google.pubsub.v1beta2.Subscription`.\n"
                + "google/pubsub/v1/pubsub.proto L880: Changed field behavior for an existing field `subscription` in message `.google.pubsub.v1beta2.GetSubscriptionRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L903: Changed field behavior for an existing field `project` in message `.google.pubsub.v1beta2.ListSubscriptionsRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L934: Changed field behavior for an existing field `subscription` in message `.google.pubsub.v1beta2.DeleteSubscriptionRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L946: Changed field behavior for an existing field `subscription` in message `.google.pubsub.v1beta2.ModifyPushConfigRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L958: Changed field behavior for an existing field `push_config` in message `.google.pubsub.v1beta2.ModifyPushConfigRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L966: Changed field behavior for an existing field `subscription` in message `.google.pubsub.v1beta2.PullRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L985: Changed field behavior for an existing field `max_messages` in message `.google.pubsub.v1beta2.PullRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L1002: Changed field behavior for an existing field `subscription` in message `.google.pubsub.v1beta2.ModifyAckDeadlineRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L1019: Changed field behavior for an existing field `ack_deadline_seconds` in message `.google.pubsub.v1beta2.ModifyAckDeadlineRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L1027: Changed field behavior for an existing field `subscription` in message `.google.pubsub.v1beta2.AcknowledgeRequest`.\n"
                + "google/pubsub/v1/pubsub.proto L1036: Changed field behavior for an existing field `ack_ids` in message `.google.pubsub.v1beta2.AcknowledgeRequest`.\n"
                + "google/pubsub/v1beta2/pubsub.proto L369: An existing field `ack_id` is removed from message `.google.pubsub.v1beta2.ModifyAckDeadlineRequest`.\n",
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
                "google/cloud/texttospeech/v1beta1/cloud_tts.proto L103: An existing value `MP3_64_KBPS` is removed from enum `AudioEncoding`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L113: An existing value `MULAW` is removed from enum `AudioEncoding`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L142: An existing enum `TimepointType` is removed.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L160: An existing field `enable_time_pointing` is removed from message `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechRequest`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L275: An existing field `timepoints` is removed from message `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L278: An existing field `audio_config` is removed from message `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto L283: An existing message `Timepoint` is removed.\n",
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
                "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing value `MP3_64_KBPS` is removed from enum `AudioEncoding`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing value `MULAW` is removed from enum `AudioEncoding`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing enum `TimepointType` is removed.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing field `enable_time_pointing` is removed from message `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechRequest`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing field `timepoints` is removed from message `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing field `audio_config` is removed from message `.google.cloud.texttospeech.v1beta1.SynthesizeSpeechResponse`.\n"
                + "google/cloud/texttospeech/v1beta1/cloud_tts.proto: An existing message `Timepoint` is removed.\n",
            )


if __name__ == "__main__":
    unittest.main()

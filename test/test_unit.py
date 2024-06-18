import io
import os
import sys
from copy import copy
from contextlib import contextmanager
from http import HTTPStatus
from unittest import TestCase

import pytest

from pipe.pipe import TeamsNotifyPipe, schema

TEST_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"


@contextmanager
def capture_output():
    standard_out = sys.stdout
    try:
        stdout = io.StringIO()
        sys.stdout = stdout
        yield stdout
    finally:
        sys.stdout = standard_out
        sys.stdout.flush()


class TeamsNotifyTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog, mocker, requests_mock):
        self.caplog = caplog
        self.mocker = mocker
        self.request_mock = requests_mock

    def setUp(self):
        self.sys_path = copy(sys.path)
        sys.path.insert(0, os.getcwd())

    def tearDown(self):
        sys.path = self.sys_path

    def test_notify_succeeded(self):
        self.mocker.patch.dict(
            os.environ, {
                'WEBHOOK_URL': TEST_WEBHOOK_URL,
                'MESSAGE': 'Hello!',
                'SUMMARY': 'Hello!'
            }
        )

        slack_status_mock = self.mocker.Mock()
        slack_status_mock.return_value.status_code = 200
        slack_status_mock.return_value.text.return_value = 'ok'

        self.request_mock.register_uri(
            'POST', TEST_WEBHOOK_URL,
            text="",
            status_code=HTTPStatus.OK
        )

        with capture_output() as out:
            TeamsNotifyPipe(pipe_schema=schema, check_for_newer_version=True).run()

        self.assertRegex(out.getvalue(), "✔ Notification successful.")

    def test_notify_failed(self):
        self.mocker.patch.dict(
            os.environ, {
                'WEBHOOK_URL': TEST_WEBHOOK_URL,
                'MESSAGE': 'Hello!'
            }
        )

        slack_status_mock = self.mocker.Mock()
        slack_status_mock.return_value.status_code = 400
        slack_status_mock.return_value.text.return_value = 'invalid_token'

        self.request_mock.register_uri(
            'POST', TEST_WEBHOOK_URL,
            text="",
            status_code=HTTPStatus.NOT_FOUND
        )

        with capture_output() as out:
            with self.assertRaises(SystemExit) as exc_context:
                TeamsNotifyPipe(pipe_schema=schema, check_for_newer_version=True).run()
            self.assertEqual(exc_context.exception.code, 1)

        self.assertRegex(out.getvalue(), "✖ Notification failed.")

    def test_notify_failed_if_no_payload_file(self):
        self.mocker.patch.dict(
            os.environ, {
                'WEBHOOK_URL': TEST_WEBHOOK_URL,
                'PAYLOAD_FILE': 'payload.json!'
            }
        )

        with capture_output() as out:
            with self.assertRaises(SystemExit) as exc_context:
                TeamsNotifyPipe(pipe_schema=schema, check_for_newer_version=True).run()
                self.assertEqual(exc_context.exception.code, 1)

        self.assertRegex(out.getvalue(), "Passed PAYLOAD_FILE path does not exist.")

    def test_notify_failed_if_both_message_and_payload(self):
        self.mocker.patch.dict(
            os.environ, {
                'WEBHOOK_URL': TEST_WEBHOOK_URL,
                'PAYLOAD_FILE': 'aaa.json!',
                'MESSAGE': 'Hello!'
            }
        )

        with capture_output() as out:
            with self.assertRaises(SystemExit) as exc_context:
                TeamsNotifyPipe(pipe_schema=schema, check_for_newer_version=True).run()
                self.assertEqual(exc_context.exception.code, 1)

        self.assertRegex(
            out.getvalue(),
            "✖ Validation errors: \nMESSAGE:\n- '''PAYLOAD_FILE'' must not be present with "
            "''MESSAGE'''\nPAYLOAD_FILE:\n- '''MESSAGE'' must not be present with ''PAYLOAD_FILE'''\n")

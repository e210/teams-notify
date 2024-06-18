# Copyright 2024 Ezio Caffi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import pathlib

import requests
import yaml
from bitbucket_pipes_toolkit import Pipe

# global variables
REQUESTS_DEFAULT_TIMEOUT = 10
BASE_SUCCESS_MESSAGE = "Notification successful"
BASE_FAILED_MESSAGE = "Notification failed"

# defines the schema for pipe variables
schema = {
    "WEBHOOK_URL": {
        "type": "string",
        "required": True
    },
    "MESSAGE": {
        "type": "string",
        "required": True,
        "excludes": "PAYLOAD_FILE"
    },
    "PAYLOAD_FILE": {
        "type": "string",
        "required": True,
        "excludes": "MESSAGE"
    },
    "TITLE": {
        "type": "string",
        "required": False,
        "excludes": "PAYLOAD_FILE"
    },
    "DEBUG": {
        "type": "boolean",
        "required": False,
        "default": False
    }

}


class TeamsNotifyPipe(Pipe):

    def __init__(self, pipe_metadata=None, pipe_schema=None, env=None, check_for_newer_version=False):
        """
        Initializes a new instance of the class.

        :param pipe_metadata: The metadata of the pipeline.
        :param pipe_schema: The schema of the pipeline.
        :param env: The environment of the pipeline.
        :param check_for_newer_version: Specifies whether to check for a newer version.
        """
        super().__init__(
            pipe_metadata=pipe_metadata,
            schema=pipe_schema,
            env=env,
            check_for_newer_version=check_for_newer_version
        )
        self.webhook_url = self.get_variable("WEBHOOK_URL")
        self.title = self.get_variable("TITLE")
        self.message = self.get_variable("MESSAGE")
        self.payload_file_path = self.get_variable("PAYLOAD_FILE")
        self.debug = self.get_variable("DEBUG")

    def get_payload(self):
        """
        Method to get the payload for a notification message.

        :return: The payload dictionary for the notification.
        """
        if self.payload_file_path:
            self.log_info("Starting with payload provided in PAYLOAD_FILE...")

            if not pathlib.Path(self.payload_file_path).exists():
                self.fail("Passed PAYLOAD_FILE path does not exist.")
        if self.title is None:
            self.title = "Notification sent from <a href='https://bitbucket.org'>Bitbucket</a>"

        self.logger.debug(f"Final TITLE: {self.title}")

        if self.payload_file_path:
            self.logger.info("Starting with payload provided in PAYLOAD_FILE...")
            if not pathlib.Path(self.payload_file_path).exists():
                self.fail("Passed PAYLOAD_FILE path does not exist.")
            try:
                with open(self.payload_file_path, 'r') as payload_file:
                    return json.loads(payload_file.read())
            except json.JSONDecodeError:
                self.fail(f'Failed to parse PAYLOAD_FILE {self.payload_file_path}: invalid JSON provided.')
        else:
            return {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "title": self.title,
                "text": self.message
            }

    def send_request(self, payload):
        """
        :param payload: The payload data to be sent in the request (Type: Any)
        :return: The response text if the request is successful, else None (Type: Optional[str])

        """
        headers = {'Content-Type': 'application/json'}
        response = None
        try:
            response = requests.post(
                url=self.webhook_url,
                headers=headers,
                json=payload,
                timeout=REQUESTS_DEFAULT_TIMEOUT
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.fail(f'{BASE_FAILED_MESSAGE}. Pipe has finished with an error: {e}')

        if response:
            return response.text
        else:
            return None

    def run(self):
        """
        Sends a notification to TEAMS and logs the response.

        :return: None
        """
        self.log_info("Sending notification to TEAMS ...")
        payload = self.get_payload()
        self.log_debug(f"Payload: {payload}")
        response_text = self.send_request(payload)
        self.log_info(f"HTTP Response: {response_text}")
        self.success(BASE_SUCCESS_MESSAGE)


if __name__ == '__main__':
    with open('/pipe.yml') as f:
        metadata = yaml.safe_load(f.read())
    pipe = TeamsNotifyPipe(pipe_metadata=metadata, pipe_schema=schema, check_for_newer_version=True)
    pipe.run()

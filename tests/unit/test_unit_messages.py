import unittest

import requests_testing

import mailpit.messages
import mailpit.message
import mailpit.api


class MessagesModelsTestCase(unittest.TestCase):
    RESPONSE = """{
        "total": 500,
        "unread": 500,
        "count": 50,
        "start": 0,
        "messages": [
            {
              "ID": "1c575821-70ba-466f-8cee-2e1cf0fcdd0f",
              "Read": false,
              "From": {
                "Name": "John Doe",
                "Address": "john@example.com"
              },
              "To": [
                {
                  "Name": "Jane Smith",
                  "Address": "jane@example.com"
                }
              ],
              "Cc": [
                {
                  "Name": "Accounts",
                  "Address": "accounts@example.com"
                }
              ],
              "Bcc": [],
              "Subject": "Message subject",
              "Created": "2022-10-03T21:35:32.228605299+13:00",
              "Size": 6144,
              "Attachments": 0
            }
        ]
    }"""
    messages: mailpit.messages.Messages = mailpit.messages.Messages.from_json(RESPONSE)
    message: mailpit.messages.Message = messages.messages[0]

    def test_messages(self):
        self.assertIsInstance(
            MessagesModelsTestCase.messages, mailpit.messages.Messages
        )
        self.assertEqual(500, MessagesModelsTestCase.messages.total)
        self.assertEqual(500, MessagesModelsTestCase.messages.unread)
        self.assertEqual(50, MessagesModelsTestCase.messages.count)
        self.assertEqual(0, MessagesModelsTestCase.messages.start)

    def test_message(self):
        self.assertIsInstance(MessagesModelsTestCase.message, mailpit.messages.Message)
        self.assertEqual(
            "1c575821-70ba-466f-8cee-2e1cf0fcdd0f", MessagesModelsTestCase.message.id
        )
        self.assertIs(False, MessagesModelsTestCase.message.read)
        self.assertEqual("Message subject", MessagesModelsTestCase.message.subject)
        self.assertEqual(
            "2022-10-03T21:35:32.228605299+13:00",
            MessagesModelsTestCase.message.created,
        )
        self.assertEqual(6144, MessagesModelsTestCase.message.size)
        self.assertEqual(0, MessagesModelsTestCase.message.attachments)

    def test_message_from(self):
        self.assertIsInstance(
            MessagesModelsTestCase.message.from_, mailpit.models.Contact
        )
        self.assertEqual("John Doe", MessagesModelsTestCase.message.from_.name)
        self.assertEqual(
            "john@example.com", MessagesModelsTestCase.message.from_.address
        )

    def test_message_to(self):
        self.assertIsInstance(
            MessagesModelsTestCase.message.to[0], mailpit.models.Contact
        )
        self.assertEqual("Jane Smith", MessagesModelsTestCase.message.to[0].name)
        self.assertEqual(
            "jane@example.com", MessagesModelsTestCase.message.to[0].address
        )

    def test_message_cc(self):
        self.assertIsInstance(self.message.cc[0], mailpit.models.Contact)
        self.assertEqual("Accounts", MessagesModelsTestCase.message.cc[0].name)
        self.assertEqual(
            "accounts@example.com", MessagesModelsTestCase.message.cc[0].address
        )

    def test_message_bcc(self):
        self.assertEqual([], MessagesModelsTestCase.message.bcc)


class MessagesAPITestCase(unittest.TestCase):
    RESPONSE = """{
        "total": 500,
        "unread": 500,
        "count": 50,
        "start": 0,
        "messages": [
            {
              "ID": "1c575821-70ba-466f-8cee-2e1cf0fcdd0f",
              "Read": false,
              "From": {
                "Name": "John Doe",
                "Address": "john@example.com"
              },
              "To": [
                {
                  "Name": "Jane Smith",
                  "Address": "jane@example.com"
                }
              ],
              "Cc": [
                {
                  "Name": "Accounts",
                  "Address": "accounts@example.com"
                }
              ],
              "Bcc": [],
              "Subject": "Message subject",
              "Created": "2022-10-03T21:35:32.228605299+13:00",
              "Size": 6144,
              "Attachments": 0
            }
        ]
    }"""

    def setUp(self) -> None:
        self.api = mailpit.api.API("https://example.com")

    @requests_testing.activate
    def test_messages_get(self):
        requests_testing.add(
            request="https://example.com/api/v1/messages",
            response=MessagesAPITestCase.RESPONSE,
        )
        messages = self.api.get_messages()
        self.assertIsInstance(messages, mailpit.messages.Messages)
        self.assertEqual(200, self.api.last_response.status_code)

    @requests_testing.activate
    def test_messages_delete(self):
        requests_testing.add(
            request="https://example.com/api/v1/messages", response={"body": "ok"}
        )
        self.api.delete_messages(["1", "2", "3"])
        self.assertEqual(200, self.api.last_response.status_code)

    def test_messages_put(self):
        self.fail()


class MessageAPITestCase(unittest.TestCase):
    RESPONSE = """{
  "ID": "d7a5543b-96dd-478b-9b60-2b465c9884de",
  "Read": true,
  "From": {
    "Name": "John Doe",
    "Address": "john@example.com"
  },
  "To": [
    {
      "Name": "Jane Smith",
      "Address": "jane@example.com"
    }
  ],
  "Cc": [],
  "Bcc": [],
  "Subject": "Message subject",
  "Date": "2016-09-07T16:46:00+13:00",
  "Text": "Plain text MIME part of the email",
  "HTML": "HTML MIME part (if exists)",
  "Size": 79499,
  "Inline": [
    {
      "PartID": "1.2",
      "FileName": "filename.gif",
      "ContentType": "image/gif",
      "ContentID": "919564503@07092006-1525",
      "Size": 7760
    }
  ],
  "Attachments": [
    {
      "PartID": "2",
      "FileName": "filename.doc",
      "ContentType": "application/msword",
      "ContentID": "",
      "Size": 43520
    }
  ]
}
    """

    def setUp(self) -> None:
        self.api = mailpit.api.API("https://example.com")

    @requests_testing.activate
    def test_message_get(self):
        requests_testing.add(
            request="https://example.com/api/v1/message/d7a5543b-96dd-478b-9b60-2b465c9884de",
            response=MessageAPITestCase.RESPONSE,
        )
        message = self.api.get_message("d7a5543b-96dd-478b-9b60-2b465c9884de")
        self.assertIsInstance(message, mailpit.message.Message)
        self.assertEqual(200, self.api.last_response.status_code)


if __name__ == "__main__":
    unittest.main()

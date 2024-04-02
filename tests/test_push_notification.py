from django.test import TestCase
from unittest.mock import patch
from casamart.notification_sender import send_push_notification


class PushNotificationTestCase(TestCase):

    @patch('casamart.notification_sender.firebase_admin.initialize_app')
    @patch('casamart.notification_sender.messaging.send')
    def test_send_push_notification(self, mock_send, mock_initialize_app):
        # Set up mock response for messaging.send
        mock_send.return_value = "mock_response"

        # Call the function to be tested
        send_push_notification("test_token", "Test Title", "Test Body")
        print("Heyyyy")
        # Assert that the messaging.send method was called with the expected arguments
        mock_send.assert_called_once()

        # Optionally, assert other conditions based on the expected behavior

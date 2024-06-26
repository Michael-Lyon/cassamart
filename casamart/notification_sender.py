import firebase_admin
from firebase_admin import credentials, messaging
from .settings import FIREBASE_ADMIN_CREDENTIALS_FILE
from .utils import convert_string_to_json

# Initialize Firebase app only if it hasn't been initialized already


def initialize_firebase_app():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            convert_string_to_json(FIREBASE_ADMIN_CREDENTIALS_FILE))
        firebase_admin.initialize_app(cred)


def send_push_notification(token: str, title: str, body: str):
    if not token:
        print("Error: Token must be provided")
        return

    initialize_firebase_app()
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
    except Exception as e:
        print(f"Error sending message: {e}")

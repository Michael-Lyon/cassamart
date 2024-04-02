import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate(
    "casamart/casamart-app-firebase-adminsdk-ovx27-edf3398b5e.json")
firebase_admin.initialize_app(cred)


def send_push_notification(token: str, title: str, body: str):
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

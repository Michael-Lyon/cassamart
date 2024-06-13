import traceback
from .models import BankDetail
from casamart.settings import PAYSTACK_SECRET
import requests
from typing import Optional, Dict, Union


class PaystackManager:
    """
    This class provides functionality to manage interactions with Paystack,
    such as getting banks and making payments.
    """

    BASE_URL = "https://api.paystack.co"
    RESOLVE_URL = "/resolve"
    TRANSFER_RECIPIENT_URL = "/transferrecipient"
    TRANSFER_URL = "/transfer"
    VERIFY_URL = "/verify"

    def __init__(self):
        self.authorization = f"Bearer {PAYSTACK_SECRET}"
        self.headers = {"Authorization": self.authorization,
                        "Content-Type": "application/json"}

    def get_banks(self) -> Optional[Dict[str, str]]:
        """Retrieves a list of banks from the Paystack API."""
        try:
            response = requests.get(self.BASE_URL + "/banks", headers=self.headers)
            data = response.json()
            if data.get('status'):
                return data['data']
        except requests.RequestException as e:
            print(f"Error retrieving banks: {e}")
        return None

    def resolve_account_number(self, account_number: int, bank_code: int) -> Optional[Dict[str, str]]:
        """
        Queries the user's account number and verifies the user details.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}{self.RESOLVE_URL}",
                headers=self.headers,
                params={"account_number": account_number,
                        "bank_code": bank_code}
            )
            data = response.json()
            if data.get('status'):
                return data['data']
        except requests.RequestException as e:
            print(f"Error resolving account number: {e}")
        return None

    def create_transfer_recipient(self, detail: BankDetail) -> Optional[str]:
        """
        Creates a transfer recipient for making transfers.
        """
        data = {
            "type": "nuban",
            "name": detail.account_name,
            "account_number": detail.account_number,
            "bank_code": detail.bank_code,
            "currency": "NGN"
        }
        try:
            response = requests.post(
                f"{self.BASE_URL}{self.TRANSFER_RECIPIENT_URL}",
                headers=self.headers,
                json=data
            )
            data = response.json()
            if data.get('status'):
                recipient_code = data['data']['recipient_code']
                detail.recipient_code = recipient_code
                detail.save()
                return detail.recipient_code
        except requests.RequestException as e:
            traceback.print_exc()
            print(f"Error creating transfer recipient: {e}")
        return None

    def transfer(self, detail: BankDetail, amount: float) -> tuple[str|None, str|None]:
        """
        Initiates a transfer.
        """
        data = {
            "source": "balance",
            "reason": "Casamart Wallet Withdrawal",
            "amount": amount,
            "recipient": detail.recipient_code
        }
        try:
            response = requests.post(
                f"{self.BASE_URL}{self.TRANSFER_URL}",
                headers=self.headers,
                json=data
            )
            data = response.json()
            if data.get('status'):
                transfer_code = data['data']['transfer_code']
                status = data['data']['status']
                return transfer_code, status
        except requests.RequestException as e:
            print(f"Error initiating transfer: {e}")
        return None, None

    # TODO: CREATE A BACKGROUND PROCESS THAT CONFIRMS/VERIFIES PAYMENTS
    def verify_transfer(self, reference: str) -> Optional[str]:
        """
        Verifies the status of a transaction.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}{self.VERIFY_URL}{reference}",
                headers=self.headers
            )
            data = response.json()
            if data.get('status'):
                return data['data']['status']
        except requests.RequestException as e:
            print(f"Error verifying transfer: {e}")
        return None

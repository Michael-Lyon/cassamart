'''
Paystack settings file.
Contains PaystackConfig class
'''
import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Determine the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a .env file in the base directory
load_dotenv(dotenv_path=BASE_DIR / '.env')

class PaystackConfig():
    '''
    PaystackConfig class.
    '''
    PAYSTACK_URL = "https://api.paystack.co"

    SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

    PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")


    PASS_ON_TRANSACTION_COST = True

    LOCAL_COST = 0.015
    INTL_COST = 0.039

    def __new__(cls):
        raise TypeError("Can not make instance of class")

'''
Paystack settings file.
Contains PaystackConfig class
'''
import os

from dotenv import load_dotenv


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


import random
import uuid
from casamart.settings import EMAIL_HOST_USER as admin_mail
from django.core.mail import send_mail
# from casamart.settings import ADMIN_USER


class UniqueRandomNumberGenerator:
   def __init__(self):
      self.generated_numbers = set()

   def generate_unique_random(self):
      while True:
         new_number = random.randint(0, 999999)
         new_number_str = f"{new_number:06d}"
         if new_number_str not in self.generated_numbers:
             self.generated_numbers.add(new_number_str)
             return new_number_str



def get_code():
   return  str(uuid.uuid1())[:6]


def send_verification_code(email, verification_code, type):
   subject = f"CASAMART Password Reset Pin"
   message = f"""
   Dear {email},
   A {type} reset has been requested on yor account.
   Your reset code is {verification_code}.
   Expires in 5 minutes
   """
   send_mail(subject, message, admin_mail, [email])


def get_code():
   gen = UniqueRandomNumberGenerator()
   return gen.generate_unique_random()

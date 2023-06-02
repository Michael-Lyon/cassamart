from django.core.mail import send_mail
from python_paystack.managers import TransactionsManager
import json
from casamart.settings import EMAIL_HOST_USER as SENDER
from store.models import Cart



def check_payment(reference: str) -> str:
    transaction_manager = TransactionsManager()
    transaction = transaction_manager.verify_transaction(transaction_reference=reference)
    transaction = json.loads(transaction.to_json())
    return transaction['status']


def send_wallet_mail(owners: dict):
    for user, amount in owners.items():
        message = f"Hello {user}\nYour wallet has been topped with NGN{amount}"
        send_mail(subject="Cassamart Wallet Top-Up",message=message,
                  from_email=SENDER, recipient_list=[user.email], fail_silently=False)
        
        
def send_order_mail(cart: Cart):
    owners = {}
    for cart_item in cart.cartitem_set.all():
        user = cart_item.product.category.store.owner
        product = cart_item.product
        owners.setdefault(user, [])
        owners[user].append(product)
        
    for user, product in owners:    
        message = f"Hello {user}\nYou have recieved a new order for {' '.join(product)}."
        send_mail(subject="Cassamart New Order",message=message,
                    from_email=SENDER, recipient_list=[user.email], fail_silently=False)
    

from rest_framework import serializers

from casamart.utils import create_response
from .models import Transaction, BankDetail


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'bank_details', 'amount',
                'transfer_code', 'status', 'created_at', 'updated_at']


class BankDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BankDetail
        fields = ['id', 'user', 'name', 'account_number',
                'bank_code', 'recipient_code']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Customize the representation here
        return create_response(data=representation, message="Created/Retrieved Successfully", status="success")

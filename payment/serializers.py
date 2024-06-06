from rest_framework import serializers

from casamart.utils import create_response
from .models import Transaction, BankDetail


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'bank_details', 'amount',
                'transfer_code', 'status', 'created_at', 'updated_at']


class BankDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankDetail
        fields = ['id', 'account_name', 'account_number',
                'bank_code', 'bank_name']


    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     return create_response(data=representation, status="success", message="Created/Retreeived Successfully")


class BankDetailInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = ['account_name', 'account_number',
                    'bank_code', 'bank_name']

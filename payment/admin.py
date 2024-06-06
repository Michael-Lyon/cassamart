from django.contrib import admin
from .models import Transaction, BankDetail



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['bank_details', 'amount',
                    'transfer_code', 'status', 'created_at', 'updated_at']
    search_fields = ['bank_details__user__username', 'transfer_code', 'status']
    list_filter = ['status', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BankDetail)
class BankDetailAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_name', 'account_number',
                    'bank_code', 'recipient_code']
    search_fields = ['user__username', 'name',
                    'account_number', 'bank_code', 'recipient_code']
    list_filter = ['bank_code']

import django.contrib

from .models import Money, MoneyTransfer, MoneyRequest
from django.contrib import admin

class money(admin.ModelAdmin):
    list_display = ['name','money', 'money_type']

class money_transfer(admin.ModelAdmin):
    list_display = ['enter_your_username','enter_destination_username', 'enter_money_to_transfer', 'money_type']

class money_request(admin.ModelAdmin):
    list_display = ['enter_your_username','enter_destination_username', 'enter_money_to_transfer', 'transfer_status', 'money_type']

admin.site.register(Money, money)
admin.site.register(MoneyTransfer, money_transfer)
admin.site.register(MoneyRequest, money_request)
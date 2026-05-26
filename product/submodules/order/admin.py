
from django.contrib import admin
from product.submodules.order.models import (
   Order
   )
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'address','total_amount', 'ordered_at']
    list_filter = ('ordered_at',)
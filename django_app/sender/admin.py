from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'count', 'datetime_created', 'get_count_of_sent', 'get_count_of_delivery', 'get_delivery_rate']
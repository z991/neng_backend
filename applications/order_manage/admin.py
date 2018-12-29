# Register your models here.
from django.contrib import admin
from .models import OrderInfo, OrderStatus, OrderGoods, ShoppingCat

admin.site.register(OrderInfo)
admin.site.register(OrderStatus)
admin.site.register(OrderGoods)
admin.site.register(ShoppingCat)
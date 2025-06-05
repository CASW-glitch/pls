# Register your models here.
from django.contrib import admin
from .models import Product, Category, Order, OrderItem, Review,CartItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(CartItem)
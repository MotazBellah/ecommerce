from django.contrib import admin
from .models import Category, Product, Cart, ShippingInfo, Purchase, Review

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(ShippingInfo)
admin.site.register(Purchase)
admin.site.register(Review)

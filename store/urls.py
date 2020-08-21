from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("categories/<int:category_id>", views.products, name="products"),
    path("products/<int:product_id>", views.item, name="item"),
    path("addItem", views.addItem, name="addItem"),
]

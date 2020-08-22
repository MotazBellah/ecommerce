from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories/<int:category_id>", views.products, name="products"),
    path("products/<int:product_id>", views.item, name="item"),
    path("addItem", views.addItem, name="addItem"),
    path("cart", views.cart_view, name="cart"),
    path("up", views.up, name="up"),
]

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
    path("quantity", views.quantity, name="quantity"),
    path("delete", views.delete, name="delete"),
    path("checkout", views.checkout, name="checkout"),
    path("get_data", views.get_data, name="get_data"),
    path("shipping_info", views.shipping_info, name="shipping"),
    path("update_shipping_info", views.update_shipping_info, name="updateShipping"),
    path("api/category", views.category_api.as_view(), name="category_list"),
    path("api/products", views.product_api.as_view(), name="product_list"),
]

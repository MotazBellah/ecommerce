from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("products/<int:category_id>", views.products, name="products"),
]

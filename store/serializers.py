from rest_framework import serializers
from .models import Category, Product

# Creater a serializer(JSON-format) for category table
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
        )

# Creater a serializer(JSON-format) for products table
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'image1',
            'image2',
            'image3',
            'image4',
            'category',
        )

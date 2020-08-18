from django.shortcuts import render
from .models import Category, Product

# Get all the category
def index(request):
    category = Category.objects.all()
    context = {
        "category": [category[0]],
    }

    return render(request, 'store/index.html', context)

# Get all the products per category
def products(request, category_id):
    items = Product.objects.filter(category=category_id)
    context = {
        'items': items,
    }

    return render(request, 'store/products.html', context)

from django.shortcuts import render
from .models import Category, Product

# Get all the category
def index(request):
    category = Category.objects.all()
    context = {
        "category": category,
    }

    return render(request, 'store/index.html', context)

# Get all the products per category
def products(request, category_id):
    items = Product.objects.filter(category=category_id)
    category = Category.objects.all()
    context = {
        'items': items,
        "category": category,
    }

    return render(request, 'store/products.html', context)


def item(request, product_id):
    view_item = Product.objects.get(pk=product_id)
    category = Category.objects.all()
    context = {
        'item': view_item,
        'category': category,
    }

    return render(request, 'store/item.html', context)

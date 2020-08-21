from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Category, Product, Cart
import json


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


def addItem(request):
    # item = Product.objects.get(pk=product_id)
    # c = Cart.objects.filter(product=item)
    data = json.loads(request.body)
    id = data.get('id')
    name = data.get('name')
    price = data.get('price')
    print('///////////////')
    print(request.is_ajax())
    print(request.body)
    print(json.loads(request.body))
    print(id)
    print(name)
    print(price)
    print('///////////////')
    return JsonResponse({'Done': 'OK'}, status=200)

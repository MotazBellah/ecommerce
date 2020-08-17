from django.shortcuts import render
from .models import Category, Product

def index(request):
    category = Category.objects.all()
    context = {
        "category": category,
    }

    return render(request, 'store/index.html', context)

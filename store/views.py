from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Category, Product, Cart, User
from django.contrib.auth import authenticate, login, logout
import json

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "store/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_anonymous:
            return render(request, "store/login.html")
        else:
            return redirect('index')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not username:
            return render(request, "store/register.html", {
                "message": "*Not username."})

        if not email:
            return render(request, "network/register.html", {
                "message": "*Not email."})

        if not password:
            return render(request, "store/register.html", {
                "message": "*Not password."})

        if password != confirmation:
            return render(request, "store/register.html", {
                "message": "*Passwords must match."})
        # Attempt to create new user
        try:
            email_already = User.objects.filter(email=email)
            if not email_already:
                user = User.objects.create_user(username, email, password)
                user.save()
            else:
                return render(request, "store/register.html", {
                "message": "*Email already taken."
            })
        except IntegrityError:
            return render(request, "store/register.html", {
                "message": "*Username already taken."
            })
        login(request, user)
        return redirect("index")
    else:
        if request.user.is_anonymous:
            return render(request, "store/register.html")
        else:
            return redirect('index')

# Get all the category
def index(request):
    category = Category.objects.all()
    items_in_cart = Cart.objects.filter(user=request.user)

    context = {
        "category": category,
        "no_of_items": len(items_in_cart),
    }

    return render(request, 'store/index.html', context)

# Get all the products per category
def products(request, category_id):
    items = Product.objects.filter(category=category_id)
    category = Category.objects.all()
    items_in_cart = Cart.objects.filter(user=request.user)

    context = {
        'items': items,
        "category": category,
        "no_of_items": len(items_in_cart),
    }

    return render(request, 'store/products.html', context)


def item(request, product_id):
    view_item = Product.objects.get(pk=product_id)
    category = Category.objects.all()
    items_in_cart = Cart.objects.filter(user=request.user)

    context = {
        'item': view_item,
        'category': category,
        "no_of_items": len(items_in_cart),
    }

    return render(request, 'store/item.html', context)


def addItem(request):
    if request.is_ajax() and request.method == "POST":
        data = json.loads(request.body)
        id = data.get('id')
        name = data.get('name')
        price = data.get('price')
        print('$$$$$$$$$$$$')
        item = Product.objects.get(pk=id)
        cart = Cart(product=item, user=request.user)
        cart.save()
        items_in_cart = Cart.objects.filter(user=request.user)

        print('///////////////')
        print(items_in_cart)
        print(len(items_in_cart))
        print('///////////////')
        return JsonResponse({'items': len(items_in_cart)}, status=200)


def cart_view(request):
    items_in_cart = Cart.objects.filter(user=request.user)
    category = Category.objects.all()
    print('///////////////')
    # print(items_in_cart[0].product.name)
    # print(items_in_cart[0].product.description)
    # print(items_in_cart[0].product.price)
    print('///////////////')

    context = {
        "no_of_items": len(items_in_cart),
        'products': items_in_cart,
        "category": category,
    }

    return render(request, 'store/cart.html', context)


def quantity(request):
    if request.is_ajax() and request.method == "POST":
        data = json.loads(request.body)
        id = data.get('id')
        value = data.get('value')

        item = Cart.objects.get(user=request.user, pk=id)
        if int(value) != item.quantity:
            item.quantity = int(value)
            item.save()

        print('///////////////')
        print(item.get_total)
        print(id)
        print(value)
        print('///////////////')
        return JsonResponse({'items': "done", 'total': item.get_total}, status=200)

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product, Cart, User, ShippingInfo, Purchase
# from .extras import transact, generate_client_token
from .scrap import ebay, olx, ebay_API, get_amazon, tinydeal
from .forms import ShippingForm
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
import json
import braintree
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=settings.BT_ENVIRONMENT,
        merchant_id=settings.BT_MERCHANT_ID,
        public_key=settings.BT_PUBLIC_KEY,
        private_key=settings.BT_PRIVATE_KEY,
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)


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
                token = Token.objects.get(user=user)
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

    paginator = Paginator(items, per_page=5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'items': page_obj.object_list,
        "category": category,
        "no_of_items": len(items_in_cart),
        "paginator": paginator,
        "page_number": int(page_number),
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
    shipping_info = ShippingInfo.objects.filter(user=request.user).first()
    total = sum((i.get_total for i in items_in_cart), 0)
    category = Category.objects.all()
    client_token = generate_client_token()
    user_address = False
    if shipping_info:
        user_address = True
    print('///////////////')
    # print(client_token)
    # print(items_in_cart[0].product.description)
    # print(items_in_cart[0].product.price)
    print('///////////////')

    context = {
        "no_of_items": len(items_in_cart),
        'products': items_in_cart,
        "category": category,
        "client_token":client_token,
        "total": total,
        "user_address": user_address,
        "shipping_info": shipping_info,
    }

    return render(request, 'store/cart.html', context)


def quantity(request):
    if request.is_ajax() and request.method == "POST":
        data = json.loads(request.body)
        id = data.get('id')
        value = data.get('value')

        item = Cart.objects.get(user=request.user, pk=id)
        total_item = Cart.objects.filter(user=request.user)
        total_price = sum((i.get_total for i in total_item), 0)
        if int(value) != item.quantity:
            item.quantity = int(value)
            item.save()

        print('///////////////')
        print(item.get_total)
        print(id)
        print(value)
        print('///////////////')
        return JsonResponse({'items': "done", 'total': item.get_total, "total_price": total_price}, status=200)


def delete(request):
    if request.is_ajax() and request.method == "POST":
        data = json.loads(request.body)
        id = data.get('id')
        item = Cart.objects.get(user=request.user, pk=id)
        item.delete()

        total_item = Cart.objects.filter(user=request.user)
        total_price = sum((i.get_total for i in total_item), 0)
        print('///////////////')
        print(data)
        print('///////////////')

        return JsonResponse({'items': "done", "total_price": total_price}, status=200)


def checkout(request):
    # items = Cart.objects.get(user=request.user)
    # client_token = generate_client_token()
    if request.method == 'POST':
        print('&&&&&&&&&&&&&&&&&&&&&&')
        total_item = Cart.objects.filter(user=request.user)
        total_price = sum((i.get_total for i in total_item), 7000)

        result = transact({
            'amount': str(total_price),
            'payment_method_nonce': request.POST['payment_method_nonce'],
            'options': {
                "submit_for_settlement": True
            }
        })
        print('^^^^^^^^^^^^^^^^^^^66')
        # print(request.POST['payment_method_nonce'])
        if result.is_success or result.transaction:
            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            print(total_item)
            for i in total_item:
                Purchase(product=i.product, quantity=i.quantity, Total_price=i.get_total, user=request.user).save()

            total_item.delete()
            # return HttpResponseRedirect(reverse("cart"))
            return JsonResponse({'items': "Done"}, status=200)
            # return redirect(url_for('show_checkout',transaction_id=result.transaction.id))
        else:
            return JsonResponse({'items': "Not"}, status=500)
        # for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        # return redirect(url_for('new_checkout'))

def shipping_info(request):
    if request.method == 'POST':
        info = ShippingInfo.objects.get(user=request.user)
        if info:
            return JsonResponse({'message': "User already have shipping info"}, status=200)

        address1 = request.POST['address1']
        address2 = request.POST.get('address2')
        phone = request.POST['phone']
        city = request.POST['city']
        zip = request.POST.get('zip')

        print('////////////////////')
        print(address1)
        print(address2)
        print(phone)
        print(city)
        print(zip)
        print('////////////////////')

        shipping_info = ShippingInfo(address1=address1, address2=address2, user=request.user,
                                    phone=phone, city=city, zip=zip)
        shipping_info.save()

        return JsonResponse({'items': "done"}, status=200)


def update_shipping_info(request):
    if request.method == 'POST':
        info = ShippingInfo.objects.get(user=request.user)
        address1 = request.POST.get('address1') or None
        address2 = request.POST.get('address2') or None
        phone = request.POST.get('phone') or None
        city = request.POST.get('city') or None
        zip = request.POST.get('zip') or None

        changed_info = False

        if address1 and address1 != info.address1:
            info.address1 = address1
            changed_info = True
        if address2 and address2 != info.address2:
            info.address2 = address2
            changed_info = True
        if phone and phone != info.phone:
            info.phone = phone
            changed_info = True
        if zip and zip != info.zip:
            info.zip = zip
            changed_info = True
        if city and city != info.city:
            info.city = city
            changed_info = True

        if changed_info:
            info.save()

        return JsonResponse({'items': "doneeeee"}, status=200)

def get_data(request):
    if request.method == 'POST':
        name = request.POST.get('product') or None
        resource = request.POST.getlist('resources')
        ebay_list = []
        tinydeal_list = []
        olx_list = []
        ebay_data = []
        if name and resource:
            for i in resource:
                if i == "ebay":
                    # print(ebay_API(name))
                    # print('HHHHH')
                    ebay_data = ebay_API(name)
                    # ebay_list = ebay(name)
                elif i == "Tinydeal":
                    tinydeal_list = tinydeal(name)
                else:
                    olx_list = olx(name)

        print("*****************")
        print(name)
        print(resource)
    context = {
        "info": tinydeal_list,
        "olx": olx_list,
        "ebay": ebay_list,
        "ebay_data": ebay_data,
    }
    return render(request, 'store/scrap_data.html', context)


class category_api(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)


class product_api(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

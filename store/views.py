from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product, Cart, User, ShippingInfo, Purchase, Review
from .extras import transact, generate_client_token, find_transaction
from .scrap import ebay, olx, ebay_API, tinydeal, souq
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
from rest_framework import filters, generics
from datetime import datetime
import re
from .geocode import getGeocodeLocation
from django.contrib import messages


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password")
            return redirect('login')

    else:
        # If the request is get, check the user
        # If not auth, then render the login page, else redirect to the main page
        if request.user.is_anonymous:
            category = Category.objects.all()
            context = {
                'category':  category
            }
            return render(request, "store/login.html", context)
        else:
            return redirect('index')


def logout_view(request):
    logout(request)
    # Inform the user
    messages.info(request, "You are logged out")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not username:
            messages.error(request, "Username is required")
            return redirect('register')

        if not email:
            messages.error(request, "Email is required")
            return redirect('register')

        if not password:
            messages.error(request, "Password is required")
            return redirect('register')

        if password != confirmation:
            messages.error(request, "Password must match")
            return redirect('register')
        # Attempt to create new user
        try:
            email_already = User.objects.filter(email=email)
            if not email_already:
                user = User.objects.create_user(username, email, password)
                user.save()
                token = Token.objects.get(user=user)
            else:
                messages.error(request, "Email is already exist")
                return redirect('register')
        except IntegrityError:
            messages.error(request, "The user is already exist")
            return redirect('register')
        # Login with defautl the backend to be ModelBackend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Logged in successfully")
        return redirect("index")
    else:
        # If the request is get, check the user
        # If not auth, then render the register page, else redirect to the main page
        if request.user.is_anonymous:
            category = Category.objects.all()
            context = {
                'category':  category
            }
            return render(request, "store/register.html", context)
        else:
            return redirect('index')


def index(request):
    # Get all the category
    category = Category.objects.all()
    # If the user is not auth, make the no. of items to be 0
    if request.user.is_authenticated:
        items_in_cart = Cart.objects.filter(user=request.user)
    else:
        items_in_cart = []

    context = {
        "category": category,
        "no_of_items": len(items_in_cart),
    }

    return render(request, 'store/index.html', context)


def products(request, category_id):
    # Get all the products per category and all category
    items = Product.objects.filter(category=category_id)
    category = Category.objects.all()
    # If the user is not auth, make the no. of items to be 0
    if request.user.is_authenticated:
        items_in_cart = Cart.objects.filter(user=request.user)
    else:
        items_in_cart = []
    # Use pagination for better UX experience and make every page show 12 items maximum
    paginator = Paginator(items, per_page=12)
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


def searched_products(request):
    category = Category.objects.all()
    items = []
    if request.user.is_authenticated:
        items_in_cart = Cart.objects.filter(user=request.user)
    else:
        items_in_cart = []
    # If the method is post, get the product's name
    # filter the product tabel for that name
    # use name__icontains for ignore case sensitive
    if request.method == "POST":
        name = request.POST['name']
        items = Product.objects.filter(name__icontains=name)

    context = {
        'items': items,
        "category": category,
        "no_of_items": len(items_in_cart),
    }

    return render(request, 'store/search.html', context)


def item(request, product_id):
    # Get the item from the table by id
    view_item = Product.objects.get(pk=product_id)
    category = Category.objects.all()
    if request.user.is_authenticated:
        items_in_cart = Cart.objects.filter(user=request.user)
    else:
        items_in_cart = []
    # Get all the comment
    comments = Review.objects.filter(product=view_item)

    context = {
        'item': view_item,
        'category': category,
        "no_of_items": len(items_in_cart),
        "comments": comments,
        "product_id": product_id,
    }

    return render(request, 'store/item.html', context)


def addItem(request):
    # Use ajax request to add product to the user cart
    # If the user is authenticated
    if request.is_ajax() and request.method == "POST":
        if request.user.is_authenticated:
            # Get the id from the request
            data = json.loads(request.body)
            id = data.get('id')
            # Get the item and add that item to the user's cart
            item = Product.objects.get(pk=id)
            cart = Cart(product=item, user=request.user)
            cart.save()
            # Update the no. of products in the user's cart
            items_in_cart = Cart.objects.filter(user=request.user)
            return JsonResponse({'items': len(items_in_cart)}, status=200)
        else:
            messages.error(request, "You are not allowed to add products")
            return redirect('login')


def cart_view(request):
    if request.user.is_authenticated:
        # Display all the product in user's cart
        items_in_cart = Cart.objects.filter(user=request.user)
        # Calculate the total price
        total = sum((i.get_total for i in items_in_cart), 0)
        category = Category.objects.all()

        context = {
            "no_of_items": len(items_in_cart),
            'products': items_in_cart,
            "category": category,
            "total": total,
        }

        return render(request, 'store/cart.html', context)
    else:
        messages.info(request, "Please log in to view the cart")
        return redirect('login')


def shipping_checkout(request):
    # If the user is auth, get all the product in his cart
    # and Calculate the total price and shipping info
    if request.user.is_authenticated:
        items_in_cart = Cart.objects.filter(user=request.user)
        total = sum((i.get_total for i in items_in_cart), 0)
        shipping_info = ShippingInfo.objects.filter(user=request.user).first()
    else:
        items_in_cart = []
        total = 0
        shipping_info = False

    category = Category.objects.all()
    # Get the client_token for braintree integration
    client_token = generate_client_token()
    # Set some Initial value related to the user's shipping info
    user_address = 0
    address = 'Initial Title'
    location = 38.685516, -101.073324
    # if the user has a shipping info, get the address(country + city + address1)
    # Get the latitude and longitude using the getGeocodeLocation function
    if shipping_info:
        user_address = 1
        address = shipping_info.get_address
        location = getGeocodeLocation(address.replace(', ', '+'))

    context = {
        "no_of_items": len(items_in_cart),
        'products': items_in_cart,
        "category": category,
        "client_token":client_token,
        "total": total,
        "user_address": user_address,
        "shipping_info": shipping_info,
        'address': address,
        'location': location,
    }

    return render(request, 'store/shipping_checkout.html', context)


def quantity(request):
    if request.is_ajax() and request.method == "POST":
        if request.user.is_authenticated:
            # Get the id of the product and the quantity in the user's cart
            data = json.loads(request.body)
            id = data.get('id')
            value = data.get('value')
            # Get the item form the user's cart, check if the value (update quantity) not equal to the item's quantity
            # then update the item
            item = Cart.objects.get(user=request.user, pk=id)
            if int(value) != item.quantity:
                item.quantity = int(value)
                item.save()
            # Get the new total price
            total_item = Cart.objects.filter(user=request.user)
            total_price = sum((i.get_total for i in total_item), 0)

            return JsonResponse({'items': "done", 'total': item.get_total, "total_price": total_price}, status=200)
        else:
            messages.error(request, "You are not allowed to do this action, please create an account or log in")
            return redirect('login')



def delete(request):
    if request.is_ajax() and request.method == "POST":
            if request.user.is_authenticated:
                # Get the id of the product and delete it
                data = json.loads(request.body)
                id = data.get('id')
                item = Cart.objects.get(user=request.user, pk=id)
                item.delete()
                # Calculate the new total price
                items_in_cart = Cart.objects.filter(user=request.user)
                total_price = sum((i.get_total for i in items_in_cart), 0)

                return JsonResponse({'items': len(items_in_cart), "total_price": total_price}, status=200)
            else:
                messages.error(request, "You are not allowed to do this action, please create an account or log in")
                return redirect('login')


def checkout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Get the total products and total price
            total_item = Cart.objects.filter(user=request.user)
            total_price = sum((i.get_total for i in total_item), 0)
            # Accept the payment using braintree
            try:
                result = transact({
                    'amount': str(round(total_price,2)),
                    'payment_method_nonce': request.POST['payment_method_nonce'],
                    'options': {
                        "submit_for_settlement": True
                    }
                })
            except Exception as e:
                print(e)
                return JsonResponse({'error': "Something went wrong"})
            # If success update the Purchase table and delete the cart
            if result.is_success or result.transaction:
                for i in total_item:
                    Purchase(product=i.product, quantity=i.quantity, Total_price=i.get_total, user=request.user).save()

                total_item.delete()

                return JsonResponse({'items': "Done"}, status=200)

            else:
                return JsonResponse({'error': "Something went wrong"})
        else:
            messages.error(request, "You are not allowed to do this action, please create an account or log in")
            return redirect('login')


def shipping_info(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Check if the user already has a shipping info
            info = ShippingInfo.objects.filter(user=request.user).first()
            if info:
                return JsonResponse({'message': "User already have shipping info"}, status=200)
            # Get the info from the user
            address1 = request.POST['address1']
            address2 = request.POST.get('address2')
            phone = request.POST['phone']
            city = request.POST['city']
            country = request.POST['country']
            zip = request.POST.get('zip')
            # Make sure the address1 not empty
            if not address1:
                return JsonResponse({'error': "address1 is required"})
            # Make sure the city not empty
            if not city:
                return JsonResponse({'error': "city is required"})
            # Make sure the country not empty
            if not country:
                return JsonResponse({'error': "country is required"})
            # Use regex to validate the phone number
            phone_regex = re.findall(r'^\+\d{9,15}$', phone)
            if not phone_regex or len(phone) > 15 or len(phone) < 7:
                return JsonResponse({'error': "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."})

            if len(str(zip)) != 5:
                return JsonResponse({'error': "The zip code must contain 5 digits."})

            # Update the shipping info, and get the latitude and longitude
            shipping_info = ShippingInfo(address1=address1, address2=address2, user=request.user,
                                        phone=phone, city=city, zip=zip, country=country)
            shipping_info.save()
            info = ShippingInfo.objects.filter(user=request.user).first()
            total_address = country.strip() + '+' + city.strip() + '+' + address1.strip()
            location = getGeocodeLocation(total_address)

            return JsonResponse({'items': "done",
                                 "info": info.serialize(),
                                 "location": location,
                                 'mapTitle': total_address.replace('+', ", ")
                                 }, status=200)
        else:
            messages.error(request, "You are not allowed to do this action, please create an account or log in")
            return redirect('login')



def update_shipping_info(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Check if the user has a shipping_info
            info = ShippingInfo.objects.filter(user=request.user).first()
            if not info:
                return JsonResponse({'error': "You don not have a shipping information yet"})
            # Get the info from the user and set the other field to be the old value
            # in case the user did not change them
            address1 = request.POST.get('address1') or info.address1
            address2 = request.POST.get('address2') or info.address2
            phone = request.POST.get('phone') or info.phone
            country = request.POST.get('country') or info.country
            city = request.POST.get('city') or info.city
            zip = request.POST.get('zip') or info.zip

            changed_info = False
            changed_location = False
            # Check if any of the shipping_info attribute changed
            if address1 and address1 != info.address1 and not address1.isspace():
                info.address1 = address1.strip()
                changed_info = True
                changed_location = True
            if address2 and address2 != info.address2 and not address2.isspace():
                info.address2 = address2
                changed_info = True
            if phone and phone != info.phone:
                # validate the phone number
                phone_regex = re.findall(r'^\+\d{9,15}$', phone)
                if not phone_regex or len(phone) > 15 or len(phone) < 7:
                    return JsonResponse({'error': "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."})
                info.phone = phone
                changed_info = True
            if zip and zip != info.zip and not zip.isspace():
                if len(str(zip)) != 5:
                    return JsonResponse({'error': "The zip code must contain 5 digits."})
                info.zip = zip
                changed_info = True
            if city and city != info.city and not city.isspace():
                info.city = city.strip()
                changed_info = True
                changed_location = True
            if country and country != info.country and not country.isspace():
                info.country = country.strip()
                changed_info = True
                changed_location = True
            # If any shipping_info attribute changed, then save it with the new values
            if changed_info:
                info.save()
            # If any of location changed (address1, city, country)
            # update the location
            if changed_location:
                location_list = [country, city, address1]
                total_address = "+".join(location_list)
                location = getGeocodeLocation(total_address)
            else:
                total_address = ''
                location = ''

            return JsonResponse({'items': "doneeeee",
                                 "info": info.serialize(),
                                 "location": location,
                                 'mapTitle': total_address.replace('+', ", ")
                                 }, status=200)
        else:
            messages.error(request, "You are not allowed to do this action, please create an account or log in")
            return redirect('login')



def get_data(request):
    name, resources = '', ''
    if request.method == 'POST':
        # Get the product name and the resource
        name = request.POST.get('product') or None
        resource = request.POST.get('resources') or None
    ebay_list = []
    tinydeal_list = []
    olx_list = []
    ebay_data = []
    souq_data = []
    another_websits = ['ebay', 'Tinydeal', 'Souq', 'OLX']
    
    if (not(len(name) == 0 or name.isspace())) and (resource in another_websits):
        if resource == "ebay":
            ebay_data = ebay_API(name)
        elif resource == "Tinydeal":
            tinydeal_list = tinydeal(name)
        elif resource == "Souq":
            souq_data = souq(name)
        else:
            olx_list = olx(name)

    context = {
        "info": tinydeal_list,
        "olx": olx_list,
        "ebay": ebay_list,
        "ebay_data": ebay_data,
        "souq_data": souq_data,
    }
    return render(request, 'store/scrap_data.html', context)


def comment_book(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # get the value from the form
            comment = request.POST['value']
            product_id = request.POST['product_id']

            # Check if the input is valid
            if len(comment) == 0 or comment.isspace():
                return JsonResponse({'error': "something went wrong!"})

            product_obj = Product.objects.get(pk=product_id)
            user_comment = Review(product=product_obj, comment=comment, user=request.user)
            user_comment.save()

            today = datetime.now()

            return JsonResponse({'user': request.user.username,
                                 'comment': comment,
                                 'date': today.strftime("%b %d %Y %H:%M %p"),
                                 'id': user_comment.id})
        else:
            messages.error(request, "You are not allowed to do this action, please create an account or log in")
            return redirect('login')


def deleteComments(request):
    if request.is_ajax() and request.method == "POST":
        if request.user.is_authenticated:
            data = json.loads(request.body)
            id = data.get('id')
            comment = Review.objects.get(user=request.user, pk=id)
            comment.delete()

            return JsonResponse({'items': "done"}, status=200)
        else:
            messages.error(request, "You are not allowed to do this action, please create an account or log in")
            return redirect('login')


def api_doc(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            t = Token.objects.filter(user=request.user).first()
            return JsonResponse({'token': t.key}, status=200)
        else:
            return JsonResponse({'error': 'Please create an account and login'})
    else:
        category = Category.objects.all()
        context = {
            'category': category,
        }

        return render(request, 'store/api.html', context)


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


class search_product_api(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

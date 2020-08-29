from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Category, Product, Cart, User
# from .extras import transact, generate_client_token
from .scrap import ebay, olx, ebay_API, get_amazon
from django.contrib.auth import authenticate, login, logout
import json
import braintree
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer

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
    total = sum((i.get_total for i in items_in_cart), 0)
    category = Category.objects.all()
    client_token = generate_client_token()
    print('///////////////')
    # print(total)
    # print(items_in_cart[0].product.description)
    # print(items_in_cart[0].product.price)
    print('///////////////')

    context = {
        "no_of_items": len(items_in_cart),
        'products': items_in_cart,
        "category": category,
        "client_token":client_token,
        "total": total
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
        result = transact({
            'amount': request.POST['amount'],
            'payment_method_nonce': request.POST['payment_method_nonce'],
            'options': {
                "submit_for_settlement": True
            }
        })
        print('^^^^^^^^^^^^^^^^^^^66')
        if result.is_success or result.transaction:
            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            return JsonResponse({'items': "done"}, status=200)
            # return redirect(url_for('show_checkout',transaction_id=result.transaction.id))
        else:
            return JsonResponse({'items': "Not"}, status=500)
        # for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        # return redirect(url_for('new_checkout'))

def Shipping_info(request):

    if request.method == 'POST':
        address1 = request.POST['address1']
        address2 = request.POST['address2']
        phone = request.POST['phone']
        city = request.POST['city']
        zip = request.POST['zip']

        print('////////////////////')
        print(address1)
        print(address2)
        print(phone)
        print(city)
        print(zip)
        print('////////////////////')

        return JsonResponse({'items': "done"}, status=200)

def amazon(request):
    # req = Request("https://www.amazon.com/s?k=labtop", headers={'User-Agent': 'Mozilla/5.0'})
    req = Request("https://www.tinydeal.com/buy/iphone.html", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    # divs = soup.find_all('div', {'class': 'r_b_c'})
    lis = soup.find_all('li', {'class': 'productListing-even'})
    print(len(lis))
    image = []
    link = []
    price = []
    info = []
    for i in lis:
        try:
            img = i.find('img', {'class': 'lazy_load'})
            p1 = i.find('span', {'class': 'productSpecialPrice'})
            p2 = i.find('span', {'class': 'normalprice'})
            anchr = i.find('a', {'class': 'p_box_title'})
            # image.append(img.attrs['data-original'])
            # link.append((anchr.get_text(), anchr.attrs['href']))
            # price.append((p1.get_text(), p2.get_text()))
            info.append((img.attrs['data-original'], anchr.get_text(), anchr.attrs['href'], p1.get_text(), p2.get_text()))
        except Exception as e:
            pass
        # print('////////////////////////')
        # print(img.attrs['data-original'])
        # print('==========')
        # print(p1.get_text())
        # print('==========')
        # print(p2.get_text())
        # print('==========')
        # print(anchr.get_text())
        # print('==========')
        # print(anchr.attrs['href'])
        # print('==========')

    context = {
        "image": image,
        "link": link,
        "price": price,
        "range": len(link),
        "info": info
    }

    # print(olx('a'))
    # print(ebay_API('a'))
    # print(get_amazon('a'))

    return render(request, 'store/amazon.html', context)

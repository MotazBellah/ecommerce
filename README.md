# Ecommerce Store
A web application for buying products online and handle online orders. Users will be able to browse the store’s categories and products, add items to their cart, and submit their orders as well as their shipping location and display it on google maps. Meanwhile, the store owners will be able to add and update menu items, and view orders that have been placed.


- https://e-storecom.herokuapp.com
- https://youtu.be/H9pLehrVsOo

## Code
- This project is written in python 3 and Django 3 framework.
- Use Bootstrap, CSS and JS in front-end

## Application Features
- Registration, Login, Logout: Site users (customers) will be able to register for your web application with a username, password, and email address. Customers should then be able to log in and log out of your website and using the Facebook authentication and GitHub auth users can use their account to login.
- Products: The web application have many categories and many product under each category
- Adding Category/Product: Using Django Admin, site administrators (store owners) will be able to add, update, and remove items on the category/product.
- Shopping Cart: Once logged in, users will be able to add products to their shopping cart, as well as delete product, increase/decrease the quantity of the products
- Shipping location: Using google maps api, User will be able to submit/update their shopping address and display it on the google maps
- Placing an Order: Once there is at least one item in a user’s shopping cart, they can place an order, and the total and integrating with the Braintree API to allow users to actually use a credit card to make a purchase during checkout.
- API: The Store API provides a simple RESTful interface with lightweight JSON-formatted responses to use many of Store's website features, including listing all the categories, listing all the products, and searching for products, using token authentication to allow the access to stors' data
- Searching for products: Scrap the data from souq website and OLX website, and use ebay API to get products from it and display the data to the user
- Searching for products: Search for product on the store

## Test Braintree integration

| Test Value       | Card Type          |
| -----------------|:------------------:|
| 378282246310005  | American Express   |
| 4111111111111111 | Visa               |

- For more information, please visit  https://developers.braintreepayments.com/reference/general/testing/ruby#avs-and-cvv/cid-responses

## Test API integration

In a RESTful API, each resource or collection of resources is identified by a unique URL

To list all categories
`https://e-storecom.herokuapp.com/api/category Authorization: Token 9054f7aa9305e012b3c2300408c3dfdf390fcddf `

To list all products
`https://e-storecom.herokuapp.com/api/products Authorization: Token 9054f7aa9305e012b3c2300408c3dfdf390fcddf `

To search for products
`https://e-storecom.herokuapp.com/api/searched-products?search=VALUE Authorization: Token 9054f7aa9305e012b3c2300408c3dfdf390fcddf `

As you notice for each URL you should add Authorization token header

- For more information, please visit  https://e-storecom.herokuapp.com/api/doc


## Clone/Run app
````
# Clone repo
$ git clone https://github.com/MotazBellah/ecommerce.git

# Install all dependencies
$ pip install -r requirements.txt

# Run
$ cd ecommerce
$ python manage.py runserver 0:8000


# Go to localhost:8000 on your web browser.
````

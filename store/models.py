from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(blank=True, null=True)


    def serialize(self):
        return {
            "name": self.name
        }


    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.FloatField(default=0.0)
    image1 = models.ImageField()
    image2 = models.ImageField(blank=True, null=True)
    image3 = models.ImageField(blank=True, null=True)
    image4 = models.ImageField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.price}"


class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, null=True, blank=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment}"



class Purchase(models.Model):
    product = models.CharField(max_length=64)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Total_price = models.FloatField(default=0.0)
    date_added = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"{self.user}, {self.product}, {self.quantity}, {self.Total_price}"



class ShippingInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address1 = models.TextField()
    address2 = models.TextField(blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17)
    city = models.CharField(max_length=20)
    zip = models.IntegerField()

    def serialize(self):
        return {
            "address1": self.address1,
            "address2": self.address2,
            "phone": self.phone,
            "city": self.city,
            "zip": self.zip,
        }

# Generated by Django 3.0.5 on 2020-08-07 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_cart_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='quantity',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]

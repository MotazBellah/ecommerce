# Generated by Django 3.0.5 on 2020-08-06 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20200806_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image1',
            field=models.ImageField(upload_to=''),
        ),
    ]

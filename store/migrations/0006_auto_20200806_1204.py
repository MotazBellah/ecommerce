# Generated by Django 3.0.5 on 2020-08-06 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20200806_0356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='image4',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
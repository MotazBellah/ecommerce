# Generated by Django 3.0.5 on 2020-08-11 18:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_auto_20200811_0322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-21 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='ordered',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='ordered_date',
        ),
        migrations.AddField(
            model_name='order',
            name='ordered_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

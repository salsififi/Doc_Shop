# Generated by Django 5.1.2 on 2024-11-14 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_shippingaddress_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='address_2',
            field=models.CharField(blank=True, help_text='Bâtiment, lieu_dit, appartement...', max_length=1024),
        ),
    ]
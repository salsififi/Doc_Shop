# Generated by Django 5.1.2 on 2024-10-17 08:19

from django.db import migrations, models
from django.utils.text import slugify


def add_slug_to_existing_products(apps, schema_model):
    Product = apps.get_model("store", "Product")
    for product in Product.objects.all():
        if not product.slug:
            base_slug = slugify(product.name)
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            product.slug = slug
            product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=128),
        ),
        migrations.RunPython(add_slug_to_existing_products),
    ]

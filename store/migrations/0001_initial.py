# Generated by Django 5.1.2 on 2024-10-17 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('price', models.FloatField(default=0.0)),
                ('stock', models.IntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='products')),
            ],
        ),
    ]

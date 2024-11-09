import stripe
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from iso3166 import countries


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("email obligatoire.")
        email = self.normalize_email(email)
        user: AbstractUser = self.model(email=email, **kwargs)
        user.set_password(password)
        stripe_customer = stripe.Customer.create(email=email)
        user.stripe_id = stripe_customer.id
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_active"] = True
        return self.create_user(email, password, **kwargs)


class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True)
    stripe_id = models.CharField(max_length=90, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


ADDRESS_FORMAT = """
{name}
{address_1}
{address_2}
{zip_code} {city}
{country}
"""


class ShippingAddress(models.Model):
    user = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=240)
    address_1 = models.CharField(max_length=1024, help_text="Voirie et numéro")
    address_2 = models.CharField(max_length=1024, help_text="Bâtiment, lieu_dit, appartement...")
    city = models.CharField(max_length=1024)
    zip_code = models.CharField(max_length=32)
    country = models.CharField(max_length=2, choices=[(country.alpha2, country.name) for country in countries])

    def __str__(self):
        data = self.__dict__.copy()
        data.update(country=self.get_country_display().upper())
        return ADDRESS_FORMAT.format(**data).strip("\n")

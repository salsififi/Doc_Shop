import stripe
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404
from iso3166 import countries

from shop import settings
from store.models import Product, Cart, Order

stripe.api_key = settings.STRIPE_API_KEY


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("email obligatoire.")
        email = self.normalize_email(email)
        user: AbstractUser = self.model(email=email, **kwargs)
        user.set_password(password)
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

    def add_to_cart(self, slug: str) -> Cart:
        product = get_object_or_404(Product, slug=slug)
        user_cart, _ = Cart.objects.get_or_create(user=self)
        order, created = Order.objects.get_or_create(user=self,
                                                     ordered=False,
                                                     product=product, )
        user_cart.nb_products += 1
        user_cart.save()
        if created:
            user_cart.orders.add(order)
            user_cart.save()
        else:
            order.quantity += 1
            order.save()

        return user_cart


ADDRESS_FORMAT = """
{name}
{address_1}
{address_2}
{zip_code} {city}
{country}
"""


class ShippingAddress(models.Model):
    user: Shopper = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=240)
    address_1 = models.CharField(max_length=1024, help_text="Voirie et numéro")
    address_2 = models.CharField(max_length=1024, help_text="Bâtiment, lieu_dit, appartement...", blank=True)
    city = models.CharField(max_length=1024)
    zip_code = models.CharField(max_length=32)
    country = models.CharField(max_length=2, choices=[(country.alpha2, country.name) for country in countries])
    default = models.BooleanField(default=False)

    def __str__(self):
        data = self.__dict__.copy()
        data.update(country=self.get_country_display().upper())
        return ADDRESS_FORMAT.format(**data).strip("\n")

    def as_dict(self) -> dict:
        """Return an address as a dict"""
        return {
            "city": self.city,
            "line1": self.address_1,
            "line2": self.address_2,
            "postal_code": self.zip_code,
            "country": self.country,
        }

    def set_default(self):
        """Set the address as default address"""
        if not self.user.stripe_id:
            raise ValueError(f"L'utilisateur {self.user.email} n'a pas encore d'identifiant Stripe.")

        self.user.addresses.update(default=False)
        self.default = True
        self.save()

        stripe.Customer.modify(
            f"{self.user.stripe_id}",
            address=self.as_dict(),
            shipping={
                "address": self.as_dict(),
                "name": self.name,
            }
        )

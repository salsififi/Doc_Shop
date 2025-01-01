from django.test import TestCase

from accounts.models import Shopper
from store.models import Product


class UserTest(TestCase):

    def setUp(self):
        Product.objects.create(
            name="Top Sneakers",
            price=29.99,
            stock=10,
            description="De top sneakers",
        )

        self.user: Shopper = Shopper.objects.create_user(
            email="toto@toto.fr",
            password="123456789",
        )

    def test_add_to_cart(self):
        self.user.add_to_cart("top-sneakers")
        self.assertEqual(self.user.cart.nb_products, 1)

from django.test import TestCase
from django.urls import reverse

from accounts.models import Shopper
from store.models import Product, Order, Cart


class TestProduct(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name="Chaussures Docstring",
            price=25,
            stock=10,
            description="De belles chaussures Docstring",
        )

    def test_product_slug_is_automatically_created(self):
        self.assertEqual(self.product.slug, "chaussures-docstring")

    def test_product_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(),
                         reverse("store:product", kwargs={"slug": self.product.slug}))


class TestCart(TestCase):

    def setUp(self):
        user = Shopper.objects.create_user(
            email="toto@toto.fr",
            password="123456pouet"
        )
        product = Product.objects.create(
            name="spaghettis",
            price=0.99,
            stock=10,
        )
        order1 = Order.objects.create(
            user=user,
            product=product,
            quantity=3,
        )
        order2 = Order.objects.create(
            user=user,
            product=product,
            quantity=2,
        )

        self.cart = Cart.objects.create(
            user=user,
        )
        self.cart.orders.add(order1, order2)
        self.cart.save()

    def test_order_is_ordered_when_cart_is_deleted(self):
        orders_pk = [order.pk for order in self.cart.orders.all()]
        self.cart.delete()
        for order_pk in orders_pk:
            order = Order.objects.get(pk=order_pk)
            self.assertTrue(order.ordered)
            self.assertIsNotNone(order.ordered_date)

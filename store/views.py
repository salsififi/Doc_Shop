from pprint import pprint

import stripe
from django.forms import modelformset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Shopper, ShippingAddress
from shop import settings
from store.forms import OrderForm
from store.models import Product, Order, Cart

stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET


def index(request: HttpRequest) -> HttpRequest:
    """Index view"""
    products = Product.objects.filter(stock__gt=0)
    return render(request,
                  template_name="store/index.html",
                  context={"products": products})


def product_detail(request: HttpRequest, slug: str) -> HttpRequest:
    """View for a product"""
    product = get_object_or_404(Product, slug=slug)
    return render(request,
                  template_name="store/detail.html",
                  context={"product": product})


def add_to_cart(request: HttpRequest, slug: str) -> HttpRequest:
    """View to add a product in the user cart"""
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    user_cart, _ = Cart.objects.get_or_create(user=user)
    order, created = Order.objects.get_or_create(user=user,
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
    return redirect(reverse("store:product", kwargs={"slug": slug}))


def cart(request: HttpRequest) -> HttpRequest:
    """User cart view"""
    orders = Order.objects.filter(user=request.user, ordered=False)
    if orders.count() == 0:
        return redirect('index')
    OrderFormSet = modelformset_factory(Order, OrderForm, extra=0)
    formset = OrderFormSet(queryset=orders)
    return render(request,
                  template_name="store/cart.html",
                  context={"forms": formset})


def update_quantities(request: HttpRequest) -> HttpRequest:
    """View when quantities are changed in the cart"""
    OrderFormSet = modelformset_factory(Order, OrderForm, extra=0)
    formset = OrderFormSet(request.POST, queryset=Order.objects.filter(user=request.user,
                                                                       ordered=False))
    if formset.is_valid():
        user_cart = request.user.cart
        new_nb_products = 0
        for form in formset:
            new_nb_products += int(form.cleaned_data["quantity"])
        user_cart.nb_products = new_nb_products
        user_cart.save()
        formset.save()
    return redirect('store:cart')


def delete_cart(request: HttpRequest) -> HttpRequest:
    """Delete user's cart content, and cart itself"""
    if user_cart := request.user.cart:
        user_cart.delete()
    return redirect('index')


def stripe_checkout_session(request: HttpRequest) -> HttpRequest | str:
    """Stripe checkout session for payments"""
    user: Shopper = request.user  # type: ignore
    user_cart = user.cart
    checkout_data = {
            "locale": "fr",
            "line_items": [
                    {"quantity": order.quantity,
                     "price": order.product.stripe_id}
                    for order in user_cart.orders.all()
                ],
            "mode": 'payment',
            "success_url": request.build_absolute_uri(reverse("store:checkout_success")),
            "cancel_url": request.build_absolute_uri(reverse("store:cart")),
            "automatic_tax": {'enabled': True},
            "shipping_address_collection": {"allowed_countries": ["FR", "CH", "US", "CA"]}
        }
    if request.user.stripe_id:
        checkout_data["customer"] = user.stripe_id
    else:
        checkout_data["customer_email"] = user.email
        checkout_data["customer_creation"] = "always"

    try:
        checkout_session = stripe.checkout.Session.create(**checkout_data)
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Receive events from Stripe"""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if (
            event['type'] == 'checkout.session.completed'
            or event['type'] == 'checkout.session.async_payment_succeeded'
    ):
        data = event['data']['object']
        try:
            user = get_object_or_404(Shopper, email=data["customer_details"]["email"])
        except KeyError:
            return HttpResponse("Invalid user email", status=404)

        complete_order(data, user)
        save_shipping_address(data, user)
        return HttpResponse(status=200)

    return HttpResponse(status=200)


def complete_order(data, user: Shopper):
    user.cart.delete()  # type: ignore
    user.save()
    return HttpResponse(status=200)


def save_shipping_address(data, user):
    """
    Save customer shipping address from Stripe
    "shipping_details": {
        "address": {
          "city": "Les Herbiers",
          "country": "FR",
          "line1": "1 Rue du Pouet",
          "line2": null,
          "postal_code": "85500",
          "state": null
        },
        "name": "POUET Simon"
    },
    """
    try:
        address = data["shipping_details"]["address"]
        name = data["shipping_details"]["name"]
        city = address["city"]
        country = address["country"]
        address_1 = address["line1"]
        address_2 = address["line2"]
        zip_code = address["postal_code"]
    except KeyError:
        return HttpResponse(status=400)

    ShippingAddress.objects.get_or_create(user=user,
                                          name=name,
                                          city=city,
                                          country=country,
                                          address_1=address_1,
                                          address_2=address_2 or "",
                                          zip_code=zip_code)
    return HttpResponse(status=200)


def checkout_success(request: HttpRequest) -> HttpRequest:
    """View when a payment is ok on Stripe"""
    return render(request, template_name="store/checkout_success.html")
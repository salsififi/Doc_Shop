from django.urls import path

from store.views import (product_detail, add_to_cart, cart, delete_cart, stripe_checkout_session,
                         checkout_success, stripe_webhook, update_quantities)

app_name = "store"

urlpatterns = [
    path('cart/', cart, name='cart'),
    path('cart/update_quantities/', update_quantities, name='update_quantities'),
    path('cart/delete/', delete_cart, name='delete_cart'),
    path('cart/stripe_checkout_session/', stripe_checkout_session, name="stripe_checkout_session"),
    path('cart/success/', checkout_success, name="checkout_success"),
    path('product/<str:slug>/', product_detail, name='product'),
    path('product/<str:slug>/add-to-cart', add_to_cart, name='add_to_cart'),
    path('stripe_webhook/', stripe_webhook, name='stripe_webhook'),
]

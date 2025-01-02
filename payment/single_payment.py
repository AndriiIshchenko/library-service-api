import stripe

from django.conf import settings
from django.urls import reverse
from stripe.checkout._session import Session


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_session(borrowing, request) -> Session:
    """
    Create a payment session for a borrowing using Stripe Checkout
    """
    try:
        success_url = request.build_absolute_uri(reverse("payment:payment-success"))
        cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Payment for {borrowing.id}",
                        },
                        "unit_amount": int(borrowing.money_to_pay * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
        )
        return session
    except Exception as e:
        raise ValueError(f"Error creating payment: {str(e)}") from e

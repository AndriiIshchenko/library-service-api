import stripe

from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_session(borrowing):
    """
    Create a payment session for a borrowing using Stripe Checkout
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Payment for {borrowing.id}",
                        },
                        "unit_amount": int(
                            borrowing.money_to_pay * 100
                        ),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://your-domain.com/success",
            cancel_url="https://your-domain.com/cancel",
        )
        return session
    except Exception as e:
        raise ValueError(f"Error creating payment: {str(e)}") from e

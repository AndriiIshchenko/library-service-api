def get_payment_serializer():
    """
    Return the PaymentSerializer class dynamicaly to avoid circular import.
    """
    from payment.serializers import PaymentSerializer
    return PaymentSerializer

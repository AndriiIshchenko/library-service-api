from django.db import IntegrityError, transaction
from rest_framework import serializers

from borrowing.models import Borrowing

from payment.models import Payment
from payment.single_payment import create_payment_session


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]
        read_only_fields = ["id", "user", "actual_return_date"]

    def create(self, validated_data) -> Borrowing:
        book = validated_data.get("book")
        # try:
        #     book = Book.objects.get(id=book_id)
        # except Book.DoesNotExist as e:
        #     raise serializers.ValidationError("Book does not exist.") from e

        if book.inventory > 0:
            try:
                with transaction.atomic():
                    book.inventory -= 1
                    book.save()
                    borrowing = Borrowing.objects.create(**validated_data)
                    payment_session = create_payment_session(borrowing)
                    Payment.objects.create(
                        borrowing=borrowing,
                        status="pending",
                        type="payment",
                        session_id=payment_session.id,
                        session_url=payment_session.url,
                        money_to_pay=borrowing.money_to_pay,
                    )
                    return borrowing
            except IntegrityError as e:
                if "expected_return_date_after_borrow_date" in str(e):
                    raise serializers.ValidationError(
                        "Expected return date must be greater than borrow date."
                    )
                raise e
        else:
            raise serializers.ValidationError("This book is out of stock.")


class BorrowingListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    payment_status = serializers.SerializerMethodField()
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "money_to_pay",
            "payment_status",
        ]
        read_only_fields = ["id", "user", "actual_return_date"]

    def get_payment_status(self, obj):
        try:
            payment = obj.payments.get()
            return payment.status
        except Payment.DoesNotExist:
            return f"Payment for this borrowing (id= {obj.id}) does not exist."


class BorrowingForPaymentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",            
        ]
        read_only_fields = ["id", "user", "actual_return_date"]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "money_to_pay",
            "payment",
        ]
        read_only_fields = ["id", "user", "actual_return_date"]

    def get_payment(self, obj):
        from payment.serializers import PaymentSerializer

        try:
            payments = obj.payments.all()
            return PaymentSerializer(payments, many=True).data
        except Payment.DoesNotExist:
            return f"Payment for this borrowing does not exist."


class BorrowingReturnBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "actual_return_date",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data) -> Borrowing:
        if instance.actual_return_date is None:
            with transaction.atomic():
                instance.actual_return_date = validated_data.get("actual_return_date")
                instance.save()
                book = instance.book
                book.inventory += 1
                book.save()
                return instance
        else:
            raise serializers.ValidationError("This book has already been returned.")

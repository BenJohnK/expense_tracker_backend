from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "category",
            "description",
            "date",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            raise serializers.ValidationError("Idempotency-Key header is required")

        # Check if already exists
        expense = Expense.objects.filter(idempotency_key=idempotency_key).first()
        if expense:
            return expense

        # Create new
        return Expense.objects.create(
            idempotency_key=idempotency_key,
            **validated_data
        )
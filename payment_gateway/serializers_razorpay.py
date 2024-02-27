from rest_framework import serializers

from payment_gateway.models import Transaction


class CreateOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField(max_length=10)

class TransactionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["payment_id","order_id","signature","amount","user"]

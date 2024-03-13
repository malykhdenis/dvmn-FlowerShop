from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from delivery.models import (Bouquet, Client, Courier, Flower, Master, Order,
                             Reason)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    class Meta:
        fields = ["id", "username", "adress", "phone_number",]
        model = Client


class ReasonSerializer(serializers.ModelSerializer):
    """Serializer for Reason model."""
    class Meta:
        fields = ["id", "name"]
        model = Reason


class FlowerSerializer(serializers.ModelSerializer):
    """Serializer for Flower model."""
    class Meta:
        fields = ["id", "name"]
        model = Flower


class BouquetSerializer(serializers.ModelSerializer):
    """Serializer for Bouquet model."""
    reasons = ReasonSerializer(many=True)
    flowers = FlowerSerializer(many=True)
    photo = Base64ImageField()

    class Meta:
        fields = ["id", "title", "reasons", "flowers", "price", "photo",]
        model = Bouquet


class MasterSerializer(serializers.ModelSerializer):
    """Serializer for Master model."""
    class Meta:
        fields = ["id", "name", "telegram_id",]
        model = Master


class CourierSerializer(serializers.ModelSerializer):
    """Serializer for Courier model."""
    class Meta:
        fields = ["id", "name", "telegram_id", "orders_count"]
        model = Courier


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    class Meta:
        fields = [
            "id",
            "client_id",
            "bouquet_id",
            "master_id",
            "courier_id",
            "total_price",
            "answer_time",
            ]
        model = Order

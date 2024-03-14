from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from delivery.models import (Bouquet, Client, Courier, Flower, Master, Order,
                             Reason)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    class Meta:
        fields = "__all__"
        model = Client


class ReasonSerializer(serializers.ModelSerializer):
    """Serializer for Reason model."""
    class Meta:
        fields = "__all__"
        model = Reason


class FlowerSerializer(serializers.ModelSerializer):
    """Serializer for Flower model."""
    class Meta:
        fields = "__all__"
        model = Flower


class BouquetSerializer(serializers.ModelSerializer):
    """Serializer for Bouquet model."""
    reasons = ReasonSerializer(many=True)
    flowers = FlowerSerializer(many=True)
    photo = Base64ImageField()

    class Meta:
        fields = "__all__"
        model = Bouquet


class MasterSerializer(serializers.ModelSerializer):
    """Serializer for Master model."""
    class Meta:
        fields = "__all__"
        model = Master


class CourierSerializer(serializers.ModelSerializer):
    """Serializer for Courier model."""
    class Meta:
        fields = "__all__"
        model = Courier
        read_only_fields = ("id", "name", "telegram_id",)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    class Meta:
        fields = "__all__"
        model = Order

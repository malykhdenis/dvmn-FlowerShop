from rest_framework import generics, mixins, viewsets

from delivery.models import Bouquet, Client, Courier, Master, Order, Reason
from .serializers import (BouquetSerializer, ClientSerializer,
                          CourierSerializer, MasterSerializer, OrderSerializer,
                          ReasonSerializer)


class CreateRetrieveUpdateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Mixins for Client."""
    pass


class ClientViewSet(CreateRetrieveUpdateViewSet):
    """ViewSet for Client model."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ReasonViewSet(generics.ListAPIView):
    """ViewSet for Reason model."""
    queryset = Reason.objects.all()
    serializer_class = ReasonSerializer


class BouquetViewSet(generics.ListAPIView):
    """ViewSet for Reason model."""
    queryset = Bouquet.objects.all()
    serializer_class = BouquetSerializer


class MasterViewSet(generics.RetrieveAPIView):
    """ViewSet for Master model."""
    queryset = Master.objects.all()
    serializer_class = MasterSerializer


class CourierViewSet(generics.RetrieveAPIView):
    """ViewSet for Master model."""
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer


class OrderViewSet(CreateRetrieveUpdateViewSet):
    """ViewSet for Client model."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

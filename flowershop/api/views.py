from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, viewsets, filters

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


class ReasonList(generics.ListAPIView):
    """ViewSet for Reason model."""
    queryset = Reason.objects.all()
    serializer_class = ReasonSerializer


class BouquetList(generics.ListAPIView):
    """ViewSet for Reason model."""
    serializer_class = BouquetSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('reasons__name',)

    def get_queryset(self):
        queryset = Bouquet.objects.all()
        price__lte = self.request.query_params.get("price__lte")
        if price__lte is not None:
            queryset = queryset.filter(price__lte=price__lte)
        return queryset


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

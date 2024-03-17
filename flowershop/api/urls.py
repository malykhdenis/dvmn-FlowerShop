from django.urls import include, path
from rest_framework import routers

from .views import (BouquetDetail, BouquetList, ClientViewSet, CourierDetail,
                    MasterDetail, OrderViewSet,
                    ConsultationViewSet, ReasonViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('clients', ClientViewSet)
router.register('orders', OrderViewSet)
router.register('consultations', ConsultationViewSet)
router.register('reasons', ReasonViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("bouquets/", BouquetList.as_view()),
    path("bouquets/<int:pk>/", BouquetDetail.as_view()),
    path("master/<int:pk>/", MasterDetail.as_view()),
    path("courier/<int:pk>/", CourierDetail.as_view()),
]

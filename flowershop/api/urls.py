from django.urls import include, path
from rest_framework import routers

from .views import BouquetList, ReasonList

app_name = 'api'

router = routers.DefaultRouter()
# router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path("", include(router.urls)),
    path("reasons", ReasonList.as_view()),
    path("bouquets/", BouquetList.as_view())
]

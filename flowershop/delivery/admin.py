from django.contrib import admin
from .models import Client, Bouquet, Courier, Flower, Master, Reason, Order, BouquetReason, BouquetFlower
# Register your models here.

admin.site.register(Client)
admin.site.register(Bouquet)
admin.site.register(Courier)
admin.site.register(Flower)
admin.site.register(Master)
admin.site.register(Reason)
admin.site.register(Order)
admin.site.register(BouquetReason)
admin.site.register(BouquetFlower)
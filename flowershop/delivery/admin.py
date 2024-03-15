from django.contrib import admin

from delivery.models import (Bouquet, BouquetFlower, BouquetReason, Client,
                             Courier, Flower, Master, Order, Reason,
                             Consultation)

admin.site.register(Consultation)



@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Reason)
class ReasonAdmin(admin.ModelAdmin):
    pass


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    pass


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    pass


@admin.register(BouquetReason)
class BouquetReasonAdmin(admin.ModelAdmin):
    pass


@admin.register(BouquetFlower)
class BouquetFlowerAdmin(admin.ModelAdmin):
    pass


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    pass


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

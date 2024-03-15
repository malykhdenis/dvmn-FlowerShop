from django.contrib import admin
from .models import Client, Bouquet, Courier, Flower, Master, Reason, Order, BouquetReason, BouquetFlower, Consultation
# Register your models here.

admin.site.register(Courier)
admin.site.register(Flower)
admin.site.register(Master)
admin.site.register(Reason)
admin.site.register(Order)
admin.site.register(Client)
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

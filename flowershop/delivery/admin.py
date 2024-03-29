from django.contrib import admin

from .models import (Client, Bouquet, Courier, Flower, Master, Reason, Order,
                     BouquetReason, BouquetFlower, Consultation)
# Register your models here.

admin.site.register(Courier)
admin.site.register(Flower)
admin.site.register(Master)
admin.site.register(Reason)
admin.site.register(Order)
admin.site.register(Client)
admin.site.register(Consultation)


class BouquetFlowerInline(admin.TabularInline):
    model = BouquetFlower
    extra = 5


class BouquetReasonInline(admin.TabularInline):
    model = BouquetReason
    extra = 5


class BouquetAdmin(admin.ModelAdmin):
    inlines = (BouquetFlowerInline, BouquetReasonInline)


admin.site.register(Bouquet, BouquetAdmin)

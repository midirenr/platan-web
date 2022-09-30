from django.contrib import admin
from .models import DeviceType, ModificationType, DetailType, PlaceOfProduction,GenerateSerialNumbers

# Register your models here.


@admin.register(DeviceType)
class AdminDeviceType(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ModificationType)
class AdminModificationType(admin.ModelAdmin):
    list_display = ('name', 'device_type')
    fields = ['device_type', 'name']


@admin.register(DetailType)
class AdminDetailType(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(PlaceOfProduction)
class AdminPlaceOfProduction(admin.ModelAdmin):
    list_display = ('name',)


'''
@admin.register(GenerateSerialNumbers)
class AdminGenerateSerialNumbers(admin.ModelAdmin):
    fields = ('device_type', 'modification_type', 'detail_type', 'place_of_production', 'count')
'''

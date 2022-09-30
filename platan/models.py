from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class GenerateSerialNumbers(models.Model):
    device_type = models.ForeignKey('DeviceType', on_delete=models.CASCADE)
    modification_type = models.ForeignKey('ModificationType', on_delete=models.CASCADE)
    detail_type = models.ForeignKey('DetailType', on_delete=models.CASCADE)
    place_of_production = models.ForeignKey('PlaceOfProduction', on_delete=models.CASCADE)
    count = models.IntegerField(default=1)


class DeviceType(models.Model):
    class Meta:
        verbose_name = 'Тип устройства'
        verbose_name_plural = 'Тип устройства'

    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class ModificationType(models.Model):
    class Meta:
        verbose_name = 'Тип модификации'
        verbose_name_plural = 'Тип модификации'

    name = models.CharField(max_length=40)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class DetailType(models.Model):
    class Meta:
        verbose_name = 'Тип изделия'
        verbose_name_plural = 'Тип изделия'

    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class PlaceOfProduction(models.Model):
    class Meta:
        verbose_name = 'Место производства'
        verbose_name_plural = 'Место производства'

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# Generated by Django 4.0.6 on 2022-07-30 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('platan', '0003_rename_device_type1_modificationtype_device_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenerateSerialNumbers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platan.devicetype')),
                ('modification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platan.modificationtype')),
            ],
        ),
    ]

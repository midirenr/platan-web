# Generated by Django 4.0.6 on 2022-07-28 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('platan', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modificationtype',
            old_name='device_type',
            new_name='device_type1',
        ),
    ]

# Generated by Django 4.0.6 on 2022-07-31 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platan', '0018_alter_generateserialnumbers_place_of_production'),
    ]

    operations = [
        migrations.AddField(
            model_name='generateserialnumbers',
            name='count',
            field=models.IntegerField(default='123'),
        ),
    ]

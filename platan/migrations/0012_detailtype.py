# Generated by Django 4.0.6 on 2022-07-31 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platan', '0011_alter_modificationtype_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
    ]

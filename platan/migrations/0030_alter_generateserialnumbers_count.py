# Generated by Django 4.1 on 2022-09-29 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platan', '0029_alter_generateserialnumbers_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generateserialnumbers',
            name='count',
            field=models.IntegerField(default=1),
        ),
    ]

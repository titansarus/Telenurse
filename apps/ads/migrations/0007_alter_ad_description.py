# Generated by Django 3.2.6 on 2022-02-14 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0006_alter_ad_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='description',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
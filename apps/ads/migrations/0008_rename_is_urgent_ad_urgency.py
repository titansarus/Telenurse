# Generated by Django 3.2.6 on 2021-12-16 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0007_ad_is_urgent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ad',
            old_name='is_urgent',
            new_name='urgency',
        ),
    ]
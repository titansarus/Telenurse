# Generated by Django 3.2.6 on 2021-12-08 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0004_auto_20211207_2147'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nursead',
            old_name='situation',
            new_name='status',
        ),
    ]

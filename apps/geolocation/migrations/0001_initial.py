# Generated by Django 3.2.6 on 2021-12-08 11:45

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ads', '0005_rename_situation_nursead_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackedPoint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('timestamp', models.DateTimeField()),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('altitude_accuracy', models.FloatField(blank=True, null=True)),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('ad', models.ForeignKey(on_delete=django.db.models.expressions.Case, to='ads.ad')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RouteLine',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('location', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326)),
                ('color', models.CharField(default='#f5365c', help_text='Use hexadecimal format like #f5365c', max_length=7, validators=[django.core.validators.RegexValidator('#[a-fA-F0-9]{6}')])),
                ('ad', models.ForeignKey(on_delete=django.db.models.expressions.Case, to='ads.ad')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
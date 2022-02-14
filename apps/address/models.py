from django.contrib.gis.db import models

from django.contrib.gis.geos import Point


class Address(models.Model):
    details = models.CharField(max_length=1024)
    location = models.PointField(default=Point(0, 0), blank=True)


import json
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.contrib.gis.geos import Point

from ..ads.models import NurseAd


class TrackedPoint(models.Model):
    id = models.AutoField(primary_key=True)
    nurse_ad = models.ForeignKey(NurseAd, on_delete=models.CASCADE)
    location = models.PointField(default=Point(0, 0), blank=True)
    timestamp = models.DateTimeField()
    altitude = models.FloatField(blank=True, null=True)
    altitude_accuracy = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.id, self.timestamp.isoformat())


class RouteLine(models.Model):
    id = models.AutoField(primary_key=True)
    nurse_ad = models.ForeignKey(NurseAd, on_delete=models.CASCADE)
    location = models.LineStringField(null=True, blank=True)
    color = models.CharField(
        max_length=7,
        default="#f5365c",
        validators=[RegexValidator("#[a-fA-F0-9]{6}")],
        help_text="Use hexadecimal format like #f5365c",
    )

    def __str__(self):
        return self.nurse_ad.nurse.username

    def get_geojson_feature(self):
        """
        Return self as GeoJSON feature instead of just plain geometry.

        Color property is used on a map to color geometry. Use only hexadecimal format.
        """

        return json.dumps(
            {
                "type": "Feature",
                "geometry": json.loads(self.location.geojson),
                "properties": {"color": self.color},
            }
        )

    @property
    def route_length(self):
        """
        Get length of the route.
        """
        geom = self.location.transform(3857, clone=True)
        return geom.length

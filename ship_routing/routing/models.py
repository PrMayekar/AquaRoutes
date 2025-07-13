from django.db import models

class GridCell(models.Model):
    row = models.IntegerField()
    col = models.IntegerField()
    
    # Maritime weather data
    wave_height = models.FloatField(help_text="Wave height in meters")
    wind_speed = models.FloatField(help_text="Wind speed in knots")
    wind_direction = models.FloatField(help_text="Wind direction in degrees")
    current_speed = models.FloatField(help_text="Current speed in knots")
    current_direction = models.FloatField(help_text="Current direction in degrees")
    visibility = models.FloatField(help_text="Visibility in nautical miles")
    precipitation = models.FloatField(help_text="Precipitation in mm/hour")
    
    # TOPSIS score - overall navigability score
    topsis_score = models.FloatField(help_text="Combined score for navigation (lower is better)")
    
    # Is this a water cell?
    is_water = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('row', 'col')
        indexes = [
            models.Index(fields=['row', 'col']),
            models.Index(fields=['is_water']),
        ]
    
    def __str__(self):
        return f"Cell ({self.row}, {self.col}): {self.topsis_score:.2f}"
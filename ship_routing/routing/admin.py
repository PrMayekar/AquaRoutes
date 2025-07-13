from django.contrib import admin
from .models import GridCell

@admin.register(GridCell)
class GridCellAdmin(admin.ModelAdmin):
    list_display = ('row', 'col', 'topsis_score', 'wave_height', 'wind_speed', 'visibility')
    list_filter = ('is_water',)
    search_fields = ('row', 'col')

# The API endpoints should be under the routing path now

from django.urls import path
from . import views
from . import auth_views  # Import the custom auth views

urlpatterns = [
    path('', views.index, name='routing_home'),  # Renamed to avoid confusion
    path('signup/', views.signup, name='signup'),  # New signup URL
    path('api/grid-data/', views.get_grid_data, name='grid_data'),
    path('api/calculate-route/', views.calculate_route, name='calculate_route'),
]
from django.contrib import admin
from django.urls import path, include
from routing import views as routing_views  # Import the views for landing page redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', routing_views.landing_page, name='landing'),  # Landing page as root URL
    path('routing/', include('routing.urls')),  # Move routing URLs under /routing/
    path('accounts/', include('django.contrib.auth.urls')),  # Django built-in auth URLs
]
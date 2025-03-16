from django.shortcuts import render, redirect
from django.contrib import messages
import folium
import geopandas as gpd
import os

def landing_page(request):
    return render(request, 'ship_routing/landing.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        return redirect('load_map')
    
    return render(request, 'ship_routing/login.html')

def map_view(request):
    m = folium.Map(location=[20, -40], zoom_start=3, tiles='CartoDB positron')
    
    map_html = m._repr_html_()
    
    return render(request, 'ship_routing/map.html', {
        'map': map_html,
    })
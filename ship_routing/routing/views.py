from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
import json
import os
from django.conf import settings
from PIL import Image
from .models import GridCell
from .utils import populate_grid_cells, shortest_path

# New function for landing page
def landing_page(request):
    """Landing page view that redirects to login if not authenticated"""
    if request.user.is_authenticated:
        return redirect('routing_home')  # Redirect to main app if logged in
    return render(request, 'routing/landing.html')

# New function for signup
def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('routing_home')
    else:
        form = UserCreationForm()
    return render(request, 'routing/signup.html', {'form': form})

# Modify existing index view to require login
@login_required(login_url='/accounts/login/')
def index(request):
    """Main view for the routing application, now with login required"""
    # Ensure grid cells are populated
    populate_grid_cells()
    
    # Get map image dimensions for display
    image_path = os.path.join(settings.BASE_DIR, 'static', 'maps', 'mapimage2.jpg')
    img = Image.open(image_path)
    map_width, map_height = img.size
    
    # Get grid dimensions
    cell_size = 5
    
    return render(request, 'routing/index.html', {
        'map_width': map_width,
        'map_height': map_height,
        'cell_size': cell_size,
    })

@csrf_exempt
def get_grid_data(request):
    """API endpoint to get all water grid cells"""
    water_cells = GridCell.objects.filter(is_water=True).values('row', 'col', 'topsis_score')
    
    # Convert to format needed by frontend
    grid_data = {
        'cells': list(water_cells),
        'cell_size': 5
    }
    
    return JsonResponse(grid_data)

@csrf_exempt
def calculate_route(request):
    """API endpoint to calculate the optimal route between two points"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        data = json.loads(request.body)
        start = (data['start_row'], data['start_col'])
        goal = (data['end_row'], data['end_col'])
        
        # Get all grid cells into a dictionary format for the algorithm
        all_cells = {(cell.row, cell.col): cell.topsis_score 
                    for cell in GridCell.objects.filter(is_water=True)}
        
        # Calculate path
        path = shortest_path(start, goal, all_cells)
        
        # Calculate total cost
        total_cost = sum(all_cells[node] for node in path) if path else 0
        
        return JsonResponse({
            'path': [{'row': r, 'col': c} for r, c in path],
            'total_cost': total_cost
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

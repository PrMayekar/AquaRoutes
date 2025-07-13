import numpy as np
import heapq
import random
from PIL import Image
from matplotlib.colors import rgb_to_hsv
from django.conf import settings
import os
from .models import GridCell

def detect_ocean_from_image(image_path):
    """Process image to identify water areas using HSV color thresholding"""
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    arr = np.array(img) / 255.0
    hsv = rgb_to_hsv(arr)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    
    # HSV thresholds for ocean detection
    ocean_mask = (H >= 0.39) & (H <= 0.56) & (S >= 0.2) & (V >= 0.2)
    
    return img, ocean_mask, width, height

def generate_random_weather_data():
    """Generate random maritime weather data"""
    return {
        'wave_height': random.uniform(0.1, 5.0),
        'wind_speed': random.uniform(0, 50.0),
        'wind_direction': random.uniform(0, 360.0),
        'current_speed': random.uniform(0, 8.0),
        'current_direction': random.uniform(0, 360.0),
        'visibility': random.uniform(0.1, 10.0),
        'precipitation': random.uniform(0, 20.0),
    }

def calculate_topsis_score(weather_data):
    """Calculate TOPSIS score based on weather data"""
    # Higher weights mean more impact on navigability (bad)
    weights = {
        'wave_height': 0.25,         # Higher waves = bad
        'wind_speed': 0.20,          # Stronger winds = bad
        'current_speed': 0.20,       # Stronger currents = bad
        'visibility': -0.25,         # Higher visibility = good (negative weight)
        'precipitation': 0.10,       # More rain = bad
    }
    
    # Calculate weighted sum (simple TOPSIS approach)
    score = 1.0  # Base score
    for key, weight in weights.items():
        # Normalize value to 0-1 range based on typical max values
        if key == 'wave_height':
            norm_value = weather_data[key] / 5.0  # Max 5m waves
        elif key == 'wind_speed':
            norm_value = weather_data[key] / 50.0  # Max 50 knots
        elif key == 'current_speed':
            norm_value = weather_data[key] / 8.0  # Max 8 knots current
        elif key == 'visibility':
            norm_value = 1.0 - (weather_data[key] / 10.0)  # Invert: lower visibility is worse
        elif key == 'precipitation':
            norm_value = weather_data[key] / 20.0  # Max 20mm/h precipitation
        
        score += norm_value * weight
    
    # Add some randomness (0.7-1.3 multiplier) for variety
    score *= random.uniform(0.7, 1.3)
    
    return max(1.0, min(10.0, score))  # Clamp between 1 and 10

def populate_grid_cells(clean_db=False):
    """Populate the database with grid cells from the map image"""
    if clean_db:
        GridCell.objects.all().delete()
    
    # Skip if database already has cells
    if GridCell.objects.exists():
        GridCell.objects.all().delete()
    
    image_path = os.path.join(settings.BASE_DIR, 'static', 'maps', 'mapimage2.jpg')
    img, ocean_mask, width, height = detect_ocean_from_image(image_path)
    
    # Grid parameters
    cell_size = 5  # Smaller grid cells as requested
    ncols = width // cell_size
    nrows = height // cell_size
    
    # Batch creation for better performance
    cells_to_create = []
    
    for r in range(nrows):
        for c in range(ncols):
            cy = int(r * cell_size + cell_size / 2)
            cx = int(c * cell_size + cell_size / 2)
            
            # Check if pixel in center of cell is ocean
            if cy < height and cx < width and ocean_mask[cy, cx]:
                # Generate random weather data
                weather_data = generate_random_weather_data()
                
                # Calculate TOPSIS score
                topsis_score = calculate_topsis_score(weather_data)
                
                cells_to_create.append(GridCell(
                    row=r,
                    col=c,
                    is_water=True,
                    topsis_score=topsis_score,
                    **weather_data
                ))
    
    # Bulk create for efficiency
    GridCell.objects.bulk_create(cells_to_create, batch_size=1000)
    
    return len(cells_to_create)

def get_neighbors(node, grid_data):
    """Get neighboring cells for Dijkstra's algorithm"""
    r, c = node
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nr, nc = r + dr, c + dc
        if (nr, nc) in grid_data:
            yield (nr, nc)

def shortest_path(start, goal, grid_data):
    """Find shortest path using Dijkstra's algorithm"""
    if start not in grid_data or goal not in grid_data:
        return []
    
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        cost, current = heapq.heappop(frontier)
        
        if current == goal:
            break
            
        for nb in get_neighbors(current, grid_data):
            new_cost = cost_so_far[current] + grid_data[nb]
            
            if nb not in cost_so_far or new_cost < cost_so_far[nb]:
                cost_so_far[nb] = new_cost
                heapq.heappush(frontier, (new_cost, nb))
                came_from[nb] = current
                
    # Reconstruct path if goal was reached
    if goal not in came_from:
        return []
        
    path, cur = [], goal
    while cur:
        path.append(cur)
        cur = came_from[cur]
        
    return path[::-1]  # Reverse to get start-to-goal path
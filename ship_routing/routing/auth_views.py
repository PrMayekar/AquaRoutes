from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def landing_page(request):
    """Landing page view"""
    return render(request, 'routing/landing.html')

# In routing/auth_views.py, modify the login_view function:

def login_view(request):
    """Login view"""
    # If user is already authenticated, redirect to index
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check if 'next' parameter exists in the request
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'routing/login.html')
    
def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('landing')
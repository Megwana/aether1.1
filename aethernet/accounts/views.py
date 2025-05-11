from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
import logging
import requests

from .models import CustomUser, Notification
from .forms import CustomUserCreationForm

# Initialize logger for debugging
logger = logging.getLogger(__name__)

@login_required
def home(request):
    notifications = Notification.objects.filter(is_read=False)
    return render(request, 'accounts/home.html', {'notifications': notifications})
    SENSOR_API_URL = "http://127.0.0.1:8000/sensors/api/sensor-data/"
    WEATHER_API_URL = "http://127.0.0.1:8000/sensors/api/weather/"

    sensor_response = requests.get(SENSOR_API_URL)
    weather_response = requests.get(WEATHER_API_URL)

    sensor_data = sensor_response.json() if sensor_response.status_code == 200 else {}
    weather_data = weather_response.json() if weather_response.status_code == 200 else {}

    return render(request, "accounts/home.html", {"sensor_data": sensor_data, "weather_data": weather_data})

def register(request):
    """ Handle user registration and notify them of pending approval """
    form = CustomUserCreationForm(request.POST) if request.method == 'POST' else CustomUserCreationForm()

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Notification.objects.create(user=user, message="Your account is pending admin approval.")
        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    """ Custom login view using correct template path """
    template_name = 'registration/login.html'

def logout_view(request):
    """ Log the user out and redirect to home """
    logout(request)
    return redirect(reverse_lazy('home'))
    
def login_view(request):
    form = AuthenticationForm(request, data=request.POST) if request.method == 'POST' else AuthenticationForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_approved:
                login(request, user)
                return redirect('home')
            messages.error(request, "Your account is not yet approved.")
        else:
            messages.error(request, "Invalid login credentials.")

            # Debugging: Log notification creation
            logger.info(f"Creating failed login notification for username: {username}")

            # Create notification for failed login
            Notification.objects.create(
                user=None,  # ✅ This should be allowed by your model
                message=f"Failed login attempt for username: {username}",
                is_read=False
            )

    return render(request, 'registration/login.html', {'form': form})



def custom_authenticate(username, password):
    """ Custom authentication to check if user is approved """
    user = authenticate(username=username, password=password)
    
    if user:
        if user.is_approved:
            return user
        logger.warning(f"Login attempt for unapproved user: {username}")
        return None

    logger.warning(f"Failed login attempt for username: {username}")
    return None

@login_required
def profile(request):
    """ Display user profile page """
    return render(request, 'accounts/profile.html')

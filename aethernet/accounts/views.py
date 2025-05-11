from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
import logging

from .models import CustomUser, Notification
from .forms import CustomUserCreationForm

# Initialize logger for debugging
logger = logging.getLogger(__name__)

@login_required
def home(request):
    """ Display unread notifications for the user """
    notifications = Notification.objects.filter(user=request.user, is_read=False).prefetch_related("user")
    return render(request, 'accounts/home.html', {'notifications': notifications})

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

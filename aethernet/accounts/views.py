from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def home(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'accounts/home.html', {'notifications': notifications})
    
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Keep user inactive until approval
            user.save()

            # Save notification in the database
            Notification.objects.create(user=user, message="Your account is pending admin approval.")

            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # ✅ Use correct path

def logout_view(request):
    logout(request)
    return redirect('/')  # Redirect to home

def custom_authenticate(username, password):
    user = authenticate(username=username, password=password)
    if user and user.is_approved:
        return user
    return None

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
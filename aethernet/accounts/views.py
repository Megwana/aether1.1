from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User stays inactive until approval
            user.save()
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
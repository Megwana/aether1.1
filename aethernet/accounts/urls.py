from django.contrib.auth import views as auth_views
from django.urls import path
from accounts.views import register, logout_view, CustomLoginView, home, profile

urlpatterns = [
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'), 
]

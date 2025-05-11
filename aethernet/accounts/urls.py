from django.urls import path
from accounts.views import register, logout_view, CustomLoginView, home

urlpatterns = [
    path('', home, name='home'),  # Home page route
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
]

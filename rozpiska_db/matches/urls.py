from django.urls import path
from . import views

urlpatterns = [
    path('matches/', views.matches, name='matches'),
]
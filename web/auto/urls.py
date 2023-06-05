from django.urls import path
from . import views

urlpatterns = [
    path('compte/', views.compte_view, name='compte'),
    path('minuteur/', views.minuteur_view, name='minuteur'),
]

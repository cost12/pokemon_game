from django.urls import path
from .views import (
    PokemonView,
)

urlpatterns = [
    path('api', PokemonView.as_view()),
]
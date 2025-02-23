from django.urls import path
from .views import (
    PokemonView,
    EnergyTypeView,
    PokemonTypeView,
)

urlpatterns = [
    path('pokemon', PokemonView.as_view()),
    path('energy_types', EnergyTypeView.as_view()),
    path('pokemon_types', PokemonTypeView.as_view()),
]
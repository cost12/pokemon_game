from pokemon.pokemon_collections import generate_attacks, generate_pokemon, generate_pokemon_cards, generate_abilities
from pokemon.pokemon_types import EnergyType, PokemonType, EnergyContainer
from pokemon.pokemon_card import Pokemon, Attack, Ability

from frozendict import frozendict

def test_generate_attacks():
    attacks = generate_attacks()
    
    for id_str, attack in attacks.items():
        assert attack.id_str == id_str
        assert isinstance(attack.attack_type, PokemonType)
        assert isinstance(attack.base_damage(), int)
        assert attack.base_damage() >= 0
        assert isinstance(attack.text, str)
        assert isinstance(attack.energy_cost, EnergyContainer)

def test_generate_pokemon():
    pokemons = generate_pokemon()

    for name, pokemon in pokemons.items():
        assert name == pokemon.name
        assert isinstance(pokemon.name, str)
        assert pokemon.evolves_from is None or isinstance(pokemon.evolves_from, Pokemon)
        assert pokemon.evolves_from is None or pokemon.get_stage() == pokemon.evolves_from.get_stage() + 1
        assert pokemon.get_stage() >= 0 and pokemon.get_stage() <= 2
        assert isinstance(pokemon.types, tuple)
        for type in pokemon.types:
            assert isinstance(type, PokemonType)

def test_generate_pokemon_cards():
    abilities= generate_abilities()
    attacks  = generate_attacks()
    pokemon  = generate_pokemon()
    cards    = generate_pokemon_cards(pokemon, attacks, abilities)

    for id_str, card in cards.items():
        assert id_str == card.id_str()
        assert isinstance(card.get_name(), str)
        assert isinstance(card.pokemon, Pokemon)
        assert isinstance(card.hit_points, int)
        assert card.hit_points > 0
        assert isinstance(card.attacks, tuple)
        for attack in card.attacks:
            assert isinstance(attack, Attack)
        assert isinstance(card.retreat_cost, int)
        assert card.retreat_cost >= 0
        assert isinstance(card.level, int)
        assert card.level >= 0 and card.level <= 102
        assert isinstance(card.abilities, tuple)
        for ability in card.abilities:
            assert isinstance(ability, Ability)
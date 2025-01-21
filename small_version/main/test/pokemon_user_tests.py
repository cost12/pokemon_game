from pokemon.user import User
from pokemon.pokemon_control import BattleController
from pokemon.pokemon_collections import generate_attacks, generate_pokemon, generate_pokemon_cards
from pokemon.pokemon_card import PokemonCard
from pokemon.pokemon_battle import Deck
from pokemon.pokemon_types import EnergyType
from pokemon.utils import tuple_to_counts

def three_cards() -> tuple[User,dict[str, PokemonCard]]:
    attacks = generate_attacks()
    pokemon = generate_pokemon()
    cards = generate_pokemon_cards(pokemon, attacks)

    initial_cards = {cards['Bulbasaur']: 2, cards['Charmander']: 1}
    user = User("name", initial_cards)
    return user, cards

def twenty_cards() -> tuple[User, dict[str, PokemonCard], list[PokemonCard]]:
    attacks = generate_attacks()
    pokemon = generate_pokemon()
    cards = generate_pokemon_cards(pokemon, attacks)

    initial_cards = [
        cards['Bulbasaur'], 
        cards['Bulbasaur'], 
        cards['Ivysaur'], 
        cards['Ivysaur'], 
        cards['Venusaur'], 
        cards['Venusaur'], 
        cards['Venusaur ex'], 
        cards['Venusaur ex'], 
        cards['Charmander'],
        cards['Charmander'],
        cards['Charmeleon'],
        cards['Charmeleon'],
        cards['Charizard'],
        cards['Charizard'],
        cards['Charizard ex'],
        cards['Charizard ex'],
        cards['Squirtle'],
        cards['Squirtle'],
        cards['Wartortle'],
        cards['Wartortle']
    ]
    user = User("name", tuple_to_counts(initial_cards))
    return user, cards, initial_cards

def test_default():
    user = User("hello")
    assert user.username == "hello"
    assert isinstance(user.cards, dict)
    assert len(user.cards) == 0
    assert user.number_of_cards() == 0
    assert isinstance(user.decks, dict)
    assert len(user.decks) == 0
    assert isinstance(user.controller, BattleController)

def test_initial_cards():
    user, cards = three_cards()
    assert len(user.cards) == 2
    assert user.number_of_cards() == 3
    assert user.number_of_copies(cards['Bulbasaur']) == 2
    assert user.number_of_copies(cards['Blastoise']) == 0

def test_add_card():
    user, cards = three_cards()

    user.add_card(cards['Bulbasaur'])
    assert user.number_of_copies(cards['Bulbasaur']) == 3
    assert user.number_of_cards() == 4

    user.add_card(cards['Ivysaur'])
    assert user.number_of_copies(cards['Ivysaur']) == 1
    assert user.number_of_cards() == 5

def test_add_cards():
    user, cards = three_cards()
    
    add = [cards['Bulbasaur'], cards['Ivysaur'], cards['Ivysaur']]
    user.add_cards(add)
    assert user.number_of_cards() == 6
    assert user.number_of_copies(cards['Bulbasaur']) == 3
    assert user.number_of_copies(cards['Ivysaur']) == 2
    
    add = [cards['Bulbasaur']]
    user.add_cards(add)
    assert user.number_of_copies(cards['Bulbasaur']) == 4
    assert user.number_of_cards() == 7

    add = []
    user.add_cards(add)
    assert user.number_of_cards() == 7

def test_add_deck():
    user, cards, initial = twenty_cards()
    deck = Deck("name", tuple(initial), (EnergyType.FIRE, EnergyType.GRASS))

    assert user.add_deck(deck)
    assert user.number_of_decks() == 1

    assert user.add_deck(deck)
    assert user.number_of_decks() == 1

    deck = Deck("name2", tuple(initial), (EnergyType.FIRE, EnergyType.GRASS))
    assert user.add_deck(deck)
    assert user.number_of_decks() == 2

    initial.append(cards['Blastoise'])
    deck = Deck("name3", tuple(initial), (EnergyType.FIRE, EnergyType.GRASS))
    assert not user.add_deck(deck)
    assert user.number_of_decks() == 2
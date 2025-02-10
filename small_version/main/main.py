from pokemon.user import User
from pokemon.pokemon_collections import generate_attacks, generate_pokemon, generate_pokemon_cards, generate_trainers
from pokemon.pokemon_battle import Deck, battle_factory
from pokemon.pokemon_types import EnergyType
from pokemon.pokemon_control import battle_control, CommandLineBattleController
import pokemon.utils as utils

def main():
    # generate pokemon/cards/data
    attacks = generate_attacks()
    pokemon = generate_pokemon()
    all_pokemon = generate_pokemon_cards(pokemon, attacks)
    all_trainers = generate_trainers()

    # choose the cards for the decks
    cards1 = [
        all_pokemon['Bulbasaur 0'],
        all_pokemon['Bulbasaur 0'],
        all_pokemon['Ivysaur 0'],
        all_pokemon['Ivysaur 0'],
        all_pokemon['Venusaur 0'],
        all_pokemon['Venusaur 0'],
        all_pokemon['Venusaur ex 0'],
        all_pokemon['Charmander 0'],
        all_pokemon['Charmander 0'],
        all_pokemon['Charmeleon 0'],
        all_pokemon['Charmeleon 0'],
        all_pokemon['Charizard 0'],
        all_pokemon['Charizard 0'],
        all_pokemon['Charizard ex 0'],
        all_trainers['Pokeball'],
        all_trainers['Pokeball'],
        all_trainers['Sabrina'],
        all_trainers['Sabrina'],
        all_trainers["Professor's Research"],
        all_trainers["Professor's Research"],
    ]

    cards2 = [
        all_pokemon['Bulbasaur 0'],
        all_pokemon['Bulbasaur 0'],
        all_pokemon['Ivysaur 0'],
        all_pokemon['Ivysaur 0'],
        all_pokemon['Venusaur 0'],
        all_pokemon['Venusaur 0'],
        all_pokemon['Venusaur ex 0'],
        all_pokemon['Squirtle 0'],
        all_pokemon['Squirtle 0'],
        all_pokemon['Wartortle 0'],
        all_pokemon['Wartortle 0'],
        all_pokemon['Blastoise 0'],
        all_pokemon['Blastoise 0'],
        all_pokemon['Blastoise ex 0'],
        all_trainers['Pokeball'],
        all_trainers['Pokeball'],
        all_trainers['Sabrina'],
        all_trainers['Sabrina'],
        all_trainers["Professor's Research"],
        all_trainers["Professor's Research"],
    ]

    # make a deck both users can use
    deck1 = Deck('deck1', tuple(cards1), (EnergyType.FIRE,EnergyType.GRASS))
    deck2 = Deck('deck2', tuple(cards2), (EnergyType.WATER,EnergyType.GRASS))

    # create users and give them cards/decks to battle with
    cards = list(all_pokemon.values())
    cards.extend(cards)
    cards.extend(all_trainers.values())
    cards.extend(all_trainers.values())
    card_dict1 = utils.tuple_to_counts(cards)
    card_dict2 = utils.tuple_to_counts(cards)
    user1 = User('p1', card_dict1)
    user2 = User('p2', card_dict2)
    ready1 = user1.add_deck(deck1)
    ready2 = user2.add_deck(deck2)
    assert ready1 and ready2

    # start the battle
    battle = battle_factory(deck1, deck2)
    battle_control(battle, CommandLineBattleController("Team 1"), CommandLineBattleController("Team 2"))

if __name__ == "__main__":
    main()
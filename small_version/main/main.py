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

    # make a list of all usable cards, and double them so each user has access to all cards 
    cards = list(all_pokemon.values())
    cards.extend(cards)

    # make a deck both users can use
    cards1 = cards[0:16]
    cards1.extend(all_trainers.values())
    cards1.extend(all_trainers.values())
    cards2 = cards[-16:]
    cards2.extend(all_trainers.values())
    cards2.extend(all_trainers.values())
    deck1 = Deck('deck1', tuple(cards1), (EnergyType.WATER,EnergyType.FIRE,EnergyType.GRASS))
    deck2 = Deck('deck2', tuple(cards2), (EnergyType.WATER,EnergyType.FIRE,EnergyType.GRASS))

    # create users and give them cards/decks to battle with
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
    battle_control(battle, CommandLineBattleController(), CommandLineBattleController())

if __name__ == "__main__":
    main()
from user import User
from pokemon_collections import generate_attacks, generate_pokemon, generate_pokemon_cards
from pokemon_battle import Deck, Battle
from pokemon_types import EnergyType

def main():
    # generate pokemon/cards/data
    attacks = generate_attacks()
    pokemon = generate_pokemon()
    all_cards = generate_pokemon_cards(pokemon,attacks)

    # make a list of all usable cards, and double them so each user has access to all cards 
    cards = list(all_cards.values())
    cards.extend(cards)

    # make a deck both users can use
    deck1 = Deck('deck1', cards[0:20], [EnergyType.WATER,EnergyType.FIRE,EnergyType.GRASS])
    deck2 = Deck('deck2', cards[-20:], [EnergyType.WATER,EnergyType.FIRE,EnergyType.GRASS])

    # create users and give them cards/decks to battle with
    user1 = User('p1', cards=cards)
    user2 = User('p2', cards=cards)
    ready1 = user1.add_deck(deck1)
    ready2 = user2.add_deck(deck2)
    assert ready1 and ready2

    # start the battle
    battle = Battle(deck1, deck2)
    

if __name__ == "__main__":
    main()
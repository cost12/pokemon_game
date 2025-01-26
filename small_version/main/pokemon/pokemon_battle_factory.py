import random

from pokemon.pokemon_card import PokemonCard

def __shuffle_deck_to_start(self, cards:list[PokemonCard]) -> list[PokemonCard]:
        basics = [card for card in cards if card.is_basic()]
        starter = random.choice(basics)
        cards.remove(starter)
        random.shuffle(cards)
        cards.insert(0,starter)
        return cards

def battle_factory(deck1, deck2, actions, state, shuffle):
    pass
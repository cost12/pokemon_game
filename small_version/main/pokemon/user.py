from pokemon.pokemon_card import PokemonCard
from pokemon.pokemon_battle import Deck
from pokemon.pokemon_control import BattleController
import pokemon.utils as utils

class User:
    """Represents a user that collects and battles with cards
    """

    def __init__(self, username:str, initial_cards:list[PokemonCard]|None=None):
        self.username = username
        self.cards = dict[PokemonCard,int]() if initial_cards is None else utils.tuple_to_counts(initial_cards)
        self.decks = dict[str,Deck]()
        self.controller = BattleController()

    def add_card(self, card:PokemonCard) -> None:
        """Adds a card to the user's collection

        :param card: The card to add
        :type card: PokemonCard
        """
        if card in self.cards:
            self.cards[card] += 1
        else:
            self.cards[card] = 1

    def add_cards(self, cards:list[PokemonCard]) -> None:
        """Adds many cards to the user's collection

        :param cards: The cards to add
        :type cards: list[PokemonCard]
        """
        for card in cards:
            self.add_card(card)

    def number_of_cards(self) -> int:
        return sum(self.cards.values())
    
    def number_of_decks(self) -> int:
        return len(self.decks)
    
    def number_of_copies(self, card:PokemonCard) -> int:
        return self.cards[card] if card in self.cards else 0

    def add_deck(self, deck:Deck) -> bool:
        """Checks whether a deck can be created with the user's cards. Returns true and adds the deck if it can be made, returns false otherwise

        :param deck: A deck of cards to add
        :type deck: Deck
        :return: True if the deck is added, false otherwise
        :rtype: bool
        """
        counts = utils.tuple_to_counts(deck.get_cards())
        for card in counts.keys():
            if counts[card] > self.number_of_copies(card):
                return False
        self.decks[deck.name] = deck
        return True
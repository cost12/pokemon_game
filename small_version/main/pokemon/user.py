from pokemon.pokemon_card import PlayingCard
from pokemon.pokemon_battle import Deck
from pokemon.pokemon_control import BattleController
import pokemon.utils as utils

class User:
    """Represents a user that collects and battles with cards
    """

    def __init__(self, username:str, initial_cards:dict[PlayingCard,int]|None=None):
        self.username = username
        self.cards = dict[PlayingCard,int]() if initial_cards is None else initial_cards
        self.decks = dict[str,Deck]()
        self.controller = BattleController()

    def add_card(self, card:PlayingCard) -> None:
        """Adds a card to the user's collection

        :param card: The card to add
        :type card: PlayingCard
        """
        if card in self.cards:
            self.cards[card] += 1
        else:
            self.cards[card] = 1

    def add_cards(self, cards:list[PlayingCard]) -> None:
        """Adds many cards to the user's collection

        :param cards: The cards to add
        :type cards: list[PlayingCard]
        """
        for card in cards:
            self.add_card(card)

    def number_of_cards(self) -> int:
        return sum(self.cards.values())
    
    def number_of_decks(self) -> int:
        return len(self.decks)
    
    def number_of_copies(self, card:PlayingCard) -> int:
        return self.cards[card] if card in self.cards else 0

    def add_deck(self, deck:Deck) -> bool:
        """Checks whether a deck can be created with the user's cards. Returns true and adds the deck if it can be made, returns false otherwise

        :param deck: A deck of cards to add
        :type deck: Deck
        :return: True if the deck is added, false otherwise
        :rtype: bool
        """
        counts = dict[PlayingCard, int](utils.tuple_to_counts(deck.get_cards()))
        for card, count in counts.items():
            if count > self.number_of_copies(card):
                return False
        self.decks[deck.name] = deck
        return True
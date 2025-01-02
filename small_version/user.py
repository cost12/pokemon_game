from pokemon_card import PokemonCard
from pokemon_battle import Deck

class User:
    """Represents a user that collects and battles with cards
    """

    def __init__(self, username:str, initial_cards:list[PokemonCard]|None=None):
        self.username = username
        self.cards = dict[PokemonCard,int]() if initial_cards is None else initial_cards
        self.decks = dict[str,Deck]()

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
        map(self.add_card, cards)

    def add_deck(self, deck:list[Deck]) -> bool:
        """Checks whether a deck can be created with the user's cards. Returns true and adds the deck if it can be made, returns false otherwise

        :param deck: A deck of cards to add
        :type deck: list[Deck]
        :return: True if the deck is added, false otherwise
        :rtype: bool
        """
        # TODO: start here
        pass
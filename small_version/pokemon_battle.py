from pokemon_card import PokemonCard
from pokemon_types import EnergyType, Condition
from pokemon_control import BattleController

import random

class CantEvolveException(Exception):
    pass

class NoCardsToDrawException(Exception):
    pass

class ActivePokemon:

    def __init__(self, card:PokemonCard):
        """Represents an active pokemon in battle

        :param card: The card to become the active pokemon
        :type card: PokemonCard
        """
        self.pokemon_cards   = [card]
        self.can_evolve      = False
        self.damage_counders = 0
        self.condition       = Condition.NONE
        self.energies        = dict[EnergyType,int]()

    def active_card(self) -> PokemonCard:
        """The card that is currently on top/ highest evolved

        :return: The card that is currently on top/ highest evolved
        :rtype: PokemonCard
        """
        return self.pokemon_cards[0]

    def evolve(self, card:PokemonCard) -> None:
        """Evolves the active pokemon

        :param card: The card to evolve to
        :type card: PokemonCard
        :raises CantEvolveException: When the active pokemon does not evolve into the card
        """
        if card.evolves_from() == self.active_card().pokemon:
            self.can_evolve = False
            self.condition = Condition.NONE
            self.pokemon_cards.insert(0, card)
        else:
            raise CantEvolveException

    def end_turn(self):
        self.can_evolve = True

    def between_turns(self):
        pass

class Deck:
    """Represents a deck of cards and energy for use in battle
    """
    DUP_LIMIT = 2

    def __init__(self, name:str, initial_cards:list[PokemonCard]|None=None, energies:list[EnergyType]|None=None, size:int=20):
        """
        :param name: Name of the deck
        :type name: str
        :param initial_cards: Cards initially present in deck, defaults to None
        :type initial_cards: list[PokemonCard] | None, optional
        :param energies: Energies initially used by deck, defaults to None
        :type energies: list[EnergyType] | None, optional
        :param size: How many cards are supposed to by in the deck for a battle, defaults to 20
        :type size: int, optional
        """
        self.name     = name
        self.cards    = [] if initial_cards is None else initial_cards
        self.energies = [] if energies      is None else energies
        self.size     = size
        
    def is_valid(self) -> bool:
        """Checks whether a deck is valid for use in a battle

        :return: true if the deck is valid, false otherwise
        :rtype: bool
        """
        if len(self.cards) != self.size: return False
        card_names = dict[str,int]()
        for card in self.cards:
            if card.pokemon_name() in card_names:
                card_names[card.pokemon_name()] += 1
                if card_names[card.pokemon_name()] > self.DUP_LIMIT:
                    return False
            else:
                card_names[card.pokemon_name()] = 1
        return True
    
    def get_cards(self) -> list[PokemonCard]:
        """Get a list of the cards used in the deck

        :return: The cards in the deck
        :rtype: list[PokemonCard]
        """
        return list(self.cards)
    
    def add_card(self, card:PokemonCard):
        """Add a card to the deck

        :param card: The card to add
        :type card: PokemonCard
        """
        self.cards.append(card)

    def remove_card(self, card:PokemonCard):
        """Remove a card from the deck

        :param card: The card to remove
        :type card: PokemonCard
        """
        if card in self.cards:
            self.cards.remove(card)

    def add_energy(self, energy:EnergyType):
        """Add an energy to the deck

        :param energy: The energy to add
        :type energy: EnergyType
        """
        self.energies.append(energy)

    def remove_energy(self, energy:EnergyType):
        """Remove an energy from the deck

        :param energy: The energy to remove
        :type energy: EnergyType
        """
        if energy in self.energies:
            self.energies.remove(energy)

class DeckSetup:
    BENCH_SIZE = 3
    INITIAL_HAND_SIZE = 5
    FUTURE_ENERGIES = 1

    def __init__(self, cards:list[PokemonCard], energies:list[EnergyType]):
        """Represents the way a deck is set during a battle

        :param cards: The pokemon cards in the deck
        :type cards: list[PokemonCard]
        :param energies: The available energy types to be used
        :type energies: list[EnergyType]
        """
        self.energies = list[EnergyType](energies)

        self.hand           = list[PokemonCard]()
        self.active         = list[ActivePokemon]()
        self.discard        = list[PokemonCard]()
        self.energy_discard = dict[EnergyType,int]()
        self.deck           = list[PokemonCard]()
        self.next_energies  = list[EnergyType]()
        self.used_supporter = False
        self.__setup(cards)

    def __setup(self, cards:list[PokemonCard]):
        """Prepare the deck by shuffling the deck and drawing the hand with at least 1 basic pokemon

        :param cards: The cards in the deck
        :type cards: list[PokemonCard]
        """
        cards = list[PokemonCard](cards)
        basic = [card for card in cards if card.is_basic()]
        self.hand.append(random.choice(basic))
        cards.remove(self.hand[0])
        random.shuffle(cards)
        self.hand.extend(cards[0:self.INITIAL_HAND_SIZE-1])
        self.deck.extend(cards[self.INITIAL_HAND_SIZE-1:])

        for _ in range(self.FUTURE_ENERGIES):
            self.__get_energy()

    def __get_energy(self) -> None:
        """Generates the next energy
        """
        self.next_energies.append(random.choice(self.energies))

    def start_turn(self, get_energy:bool=True) -> None:
        """Updates the deck for a new turn

        :param get_energy: True if the player gets an energy this turn. This is only false for the first player's first turn, defaults to True
        :type get_energy: bool, optional
        :raises NoCardsToDrawException: When there are no cards left in the deck
        """
        self.used_supporter = False
        if get_energy:
            self.__get_energy()
        self.draw_card()

    def draw_card(self) -> None:
        """Updates the deck for a drawn card

        :raises NoCardsToDrawException: When there are no cards left in the deck
        """
        if len(self.deck) == 0:
            raise NoCardsToDrawException
        self.hand.append(self.deck[0])
        self.deck = self.deck[1:]

    def play_card(self):
        pass

    def retreat(self):
        pass

    def shuffle_hand_into_deck(self):
        pass

    def discard_card(self, card):
        pass

class Battle:
    """Represents a battle between two decks of cards
    """
    DECK_SIZE = 20

    def __init__(self, deck1:Deck, deck2:Deck, controller1:BattleController, controller2:BattleController):
        assert self.DECK_SIZE == deck1.size and deck1.is_valid()
        assert self.DECK_SIZE == deck2.size and deck2.is_valid()

        self.deck1 = DeckSetup(deck1.cards, deck1.energies)
        self.deck2 = DeckSetup(deck2.cards, deck2.energies)

        self.controller1 = controller1
        self.controller2 = controller2

        self.turn_number = 0

        self.team1_points = 0
        self.team2_points = 0

    def start_battle(self):
        pass
    
    def end_turn(self):
        pass

    def play_from_hand(self):
        pass

    def attack(self):
        pass

    def retreat(self):
        pass
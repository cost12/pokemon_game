from pokemon_card import PokemonCard
from pokemon_types import EnergyType, Condition

import random

class CantEvolveException(Exception):
    pass

class ActivePokemon:
    """Represents an active pokemon in battle
    """

    def __init__(self, card:PokemonCard):
        self.pokemon_card    = card
        self.can_evolve      = False
        self.damage_counders = 0
        self.condition       = Condition.NONE
        self.energies        = dict[EnergyType,int]()

    def evolve(self, card:PokemonCard) -> None:
        if card.evolves_from() == self.pokemon_card.pokemon:
            self.can_evolve = False
            self.condition = Condition.NONE
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
    """Represents the way a deck is set during a battle
    """
    BENCH_SIZE = 3
    INITIAL_HAND_SIZE = 5

    def __init__(self, cards:list[PokemonCard], energies:list[EnergyType]):
        self.energies = list[EnergyType](energies)

        self.hand           = list[PokemonCard]()
        self.active         = list[ActivePokemon]()
        self.discard        = list[PokemonCard]()
        self.energy_discard = dict[EnergyType,int]()
        self.deck           = list[PokemonCard]()
        self.next_energies  = list[EnergyType]()
        self.__setup(cards)

    def __setup(self, cards:list[PokemonCard]):
        cards = list[PokemonCard](cards)
        basic = [card for card in cards if card.is_basic()]
        self.hand.append(random.choice(basic))
        cards.remove(self.hand[0])
        random.shuffle(cards)
        self.hand.extend(cards[0:self.INITIAL_HAND_SIZE-1])
        self.deck.extend(cards[self.INITIAL_HAND_SIZE-1:])

        self.next_energies.append(random.choice(self.energies))

class Battle:
    """Represents a battle between two decks of cards
    """
    DECK_SIZE = 20

    def __init__(self, deck1:Deck, deck2:Deck):
        assert self.DECK_SIZE == deck1.size and deck1.is_valid()
        assert self.DECK_SIZE == deck2.size and deck2.is_valid()

        self.deck1 = DeckSetup(deck1.cards, deck1.energies)
        self.deck2 = DeckSetup(deck2.cards, deck2.energies)

        self.turn_number = 0

        self.team1_points = 0
        self.team2_points = 0
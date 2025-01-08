from pokemon_card import PokemonCard
from pokemon_types import EnergyType, Condition
from pokemon_control import BattleController

import random
from frozendict import frozendict
from dataclasses import dataclass, field

class CantEvolveException(Exception):
    pass

class NoCardsToDrawException(Exception):
    pass

class CantRetreatException(Exception):
    pass

@dataclass(frozen=True)
class ActivePokemon:
    pokemon_cards:tuple[PokemonCard]
    can_evolve_this_turn:bool=False
    damage:int=0
    condition:Condition=field(default=Condition.NONE)
    energies:frozendict[EnergyType,int]=field(default=frozendict[EnergyType,int]())

    def active_card(self) -> PokemonCard:
        """The card that is currently on top/ highest evolved

        :return: The card that is currently on top/ highest evolved
        :rtype: PokemonCard
        """
        return self.pokemon_cards[0]

    def evolve(self, card:PokemonCard) -> 'ActivePokemon'|None:
        """Evolves the active pokemon

        :param card: The card to evolve to
        :type card: PokemonCard
        :raises CantEvolveException: When the active pokemon does not evolve into the card
        :return: None if the card can't evolve, or the evolved card
        :rtype: ActivePokemon|None
        """
        if self.can_evolve():
            self.can_evolve_this_turn = False
            self.condition = Condition.NONE
            return ActivePokemon((card, *self.pokemon_cards), self.can_evolve_this_turn, self.damage, self.condition, self.energies)
        else:
            raise CantEvolveException
        
    def can_evolve(self, card:PokemonCard) -> bool:
        """Checks whether the active card can evolve into the given card

        :param card: The card to evolve into
        :type card: PokemonCard
        :return: True if the evolution is possible
        :rtype: bool
        """
        return self.can_evolve_this_turn and card.evolves_from() == self.active_card().pokemon

    def end_turn(self) -> 'ActivePokemon':
        """Completes the actions that happen when a turn ends

        :return: The ActivePokemon after the turn ends
        :rtype: ActivePokemon
        """
        return ActivePokemon(self.pokemon_cards, True, self.damage, self.condition, self.energies)

    def between_turns(self):
        pass

    def attach_energy(self, energy:EnergyType) -> 'ActivePokemon':
        """Adds an energy to the card

        :param energy: The type of energy to attach
        :type energy: EnergyType
        :return: The ActivePokemon after the energy is attached
        :rtype: ActivePokemon
        """
        energy_dict = dict(self.energies)
        if energy in energy_dict:
            energy_dict[energy] += 1
        else:
            energy_dict[energy] = 1
        return ActivePokemon(self.pokemon_cards, self.can_evolve_this_turn, self.damage, self.condition, frozendict(energy_dict))

    def retreat(self, energies:dict[EnergyType,int]) -> 'ActivePokemon':
        """Discards the required energies and returns true if it can retreat, otherwise returns false

        :param energies: The energies to discard
        :type energies: dict[EnergyType,int]
        :raises CantRetreatException: When the pokemon can't retreat by discarding the given energies
        :return: The resulting ActivePokemon
        :rtype: ActivePokemon
        """
        if self.can_retreat(energies):
            energies_dict = dict(self.energies)
            for energy in energies:
                energies_dict[energy] -= energies[energy]
            return ActivePokemon(self.pokemon_cards, self.can_evolve_this_turn, self.damage, self.condition, frozendict(energies_dict))
        raise CantRetreatException()

    def can_retreat(self, energies:dict[EnergyType,int]) -> bool:
        """Determines weather the active pokemon can retreat for the given cost. Checks conditions, retreat cost, and energy types

        :param energies: The energies to discard in order to retreat, must have the same energies attached to the card
        :type energies: dict[EnergyType,int]
        :return: True if the card can retreat, false otherwise
        :rtype: bool
        """
        total = 0
        for energy in energies:
            if energy not in self.energies or energies[energy] > self.energies[energy]:
                return False
            total += energies[energy]
        return total == self.active_card().retreat_cost

    def get_energies(self) -> dict[EnergyType,int]:
        """Return the energies attached to the pokemon

        :return: A dict of the energies attached to the active pokemon
        :rtype: dict[EnergyType,int]
        """
        return dict(self.energies)

    def get_cards(self) -> list[PokemonCard]:
        """Returns the cards in the active evolution

        :return: The cards in the active evolution
        :rtype: list[PokemonCard]
        """
        return list(self.pokemon_cards)

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

@dataclass(frozen=True)
class DeckView:
    active: tuple[ActivePokemon]
    hand_size: int
    deck_size: int
    energy_queue: tuple[EnergyType]
    discard_pile: tuple[PokemonCard]
    energy_discard: frozendict[EnergyType,int]

class DeckSetup:
    BENCH_SIZE = 3
    INITIAL_HAND_SIZE = 5
    MAX_HAND_SIZE = 10
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
        if len(self.deck) == 0 or len(self.hand) == self.MAX_HAND_SIZE:
            raise NoCardsToDrawException
        self.hand.append(self.deck[0])
        self.deck = self.deck[1:]

    def play_card_from_hand(self, hand_index:int):
        """Updates the deck to represent a card from the hand being used

        :param hand_index: The index in the hand of the card used
        :type hand_index: int
        """
        self.discard.append(self.hand[hand_index])
        self.hand.pop(hand_index)

    def evolve(self, hand_index:int, active_index:int) -> None:
        """Updates the deck to represent evolving a card from the hand onto an active pokemomn

        :param hand_index: The index of the card in the hand
        :type hand_index: int
        :param active_index: The index of the card in the active area
        :type active_index: int
        :raises CantEvolveException: When the pokemon can't evolve
        """
        self.active[active_index].evolve(self.hand[hand_index])
        self.hand.pop(hand_index)

    def retreat(self, active_index:int, energies:dict[EnergyType,int]) -> bool:
        """Updates the card to represent the active pokemon retreating

        :param active_index: The index of the new card to put out
        :type active_index: int
        :param energies: The energies to discard if the retreat is successful
        :type energies: dict[EnergyType,int]
        :return: True if the retreat was successful
        :rtype: bool
        """
        if active_index == 0: return False
        if self.active[active_index].retreat(energies):
            self.__discard_energies(energies)
            temp = self.active[0]
            self.active[0] = self.active[active_index]
            self.active[active_index] = temp
            return True
        return False

    def __discard_energies(self, energies:dict[EnergyType,int]) -> None:
        """Adds energies to the discard pile

        :param energies: The energies to discard
        :type energies: dict[EnergyType,int]
        """
        for energy in energies:
            if energy in self.energy_discard:
                self.energy_discard[energy] += energies[energy]
            else:
                self.energy_discard[energy] = energies[energy]

    def shuffle_hand_into_deck(self) -> None:
        """Empties the hand into the deck
        """
        self.deck.extend(self.hand)
        self.hand = []
        random.shuffle(self.deck)

    def discard_from_active(self, active_index:int) -> None:
        """Places the cards and energies from the active pokemon into the discard pile

        :param active_index: The index of the pokemon to discard
        :type active_index: int
        """
        self.discard.extend(self.active[active_index].get_cards())
        energies = self.active[active_index].get_energies()
        self.__discard_energies(energies)
        self.active.pop(active_index)

    def play_basic(self, hand_index:int) -> bool:
        """Plays a basic card from the hand to a new spot on the bench

        :param hand_index: The index of the card in the hand
        :type hand_index: int
        :return: True if the card can be placed on the bench, false otherwise
        :rtype: bool
        """
        if self.hand[hand_index].is_basic() and len(self.active) - 1 < self.BENCH_SIZE:
            self.active.append(self.hand[hand_index])
            self.hand.pop(hand_index)
            return True
        return False

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
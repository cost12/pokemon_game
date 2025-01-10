from pokemon_card import PokemonCard
from pokemon_types import EnergyType, Condition

import random
from frozendict import frozendict
from dataclasses import dataclass, field
from typing import Optional

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

    def evolve(self, card:PokemonCard) -> Optional['ActivePokemon']:
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

    def hp(self) -> int:
        """The remaining health of the pokemon

        :return: The remaining health of the pokemon
        :rtype: int
        """
        return self.active_card().hit_points - self.damage

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

@dataclass(frozen=True)
class Deck:
    name:str
    cards:tuple[PokemonCard]
    energies:tuple[EnergyType]
    
    def get_cards(self) -> tuple[PokemonCard]:
        """Get a list of the cards used in the deck

        :return: The cards in the deck
        :rtype: list[PokemonCard]
        """
        return self.cards

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

@dataclass(frozen=True)
class OpponentDeckView:
    active: tuple[ActivePokemon]
    hand_size: int
    deck_size: int
    energy_queue: tuple[EnergyType]
    discard_pile: tuple[PokemonCard]
    energy_discard: frozendict[EnergyType,int]
    bench_size: int

@dataclass(frozen=True)
class OwnDeckView:
    active: tuple[ActivePokemon]
    hand: tuple[PokemonCard]
    deck_size: int
    energy_queue: tuple[EnergyType]
    discard_pile: tuple[PokemonCard]
    energy_discard: frozendict[EnergyType,int]
    bench_size: int

def get_opponent_deck_view(deck:DeckSetup) -> OpponentDeckView:
    """Get a view of a DeckSetup without the ability to change the DeckSetup

    :param deck: The deck to view
    :type deck: DeckSetup
    :return: The immutable partial view of the deck
    :rtype: DeckView
    """
    return OpponentDeckView(tuple(deck.active), len(deck.hand), len(deck.deck), tuple(deck.next_energies), tuple(deck.discard), frozendict(deck.energy_discard), deck.BENCH_SIZE)

def get_own_deck_view(deck:DeckSetup) -> OpponentDeckView:
    """Get a view of a DeckSetup without the ability to change the DeckSetup

    :param deck: The deck to view
    :type deck: DeckSetup
    :return: The immutable partial view of the deck
    :rtype: DeckView
    """
    return OwnDeckView(tuple(deck.active), tuple(deck.hand), len(deck.deck), tuple(deck.next_energies), tuple(deck.discard), frozendict(deck.energy_discard), deck.BENCH_SIZE)

class Battle:
    """Represents a battle between two decks of cards
    """
    DECK_SIZE:int = 20
    DUPLICATE_LIMIT:int = 2
    BASIC_REQUIRED:bool = True
    POINTS_TO:int = 3

    def __init__(self, deck1:Deck, deck2:Deck):
        assert self.__deck_is_valid(deck1)
        assert self.__deck_is_valid(deck2)

        self.deck1 = DeckSetup(deck1.cards, deck1.energies)
        self.deck2 = DeckSetup(deck2.cards, deck2.energies)

        self.turn_number = 0

        self.team1_points = 0
        self.team2_points = 0

        self.team1_ready = False
        self.team2_ready = False

    def team_turn(self) -> int:
        return self.turn_number % 2

    def is_over(self) -> bool:
        return self.team1_points >= self.POINTS_TO or self.team2_points >= self.POINTS_TO

    def __deck_is_valid(self, deck:Deck) -> bool:
        """Checks whether a deck is valid for use in a battle

        :param deck: The deck to check
        :type deck: Deck 
        :return: true if the deck is valid, false otherwise
        :rtype: bool
        """
        if not (len(deck.cards) == self.DECK_SIZE):
            return False
        has_basic = False
        card_names = dict[str,int]()
        for card in deck.cards:
            if card.is_basic():
                has_basic = True
            if card.name() in card_names:
                card_names[card.name()] += 1
                if card_names[card.name()] > self.DUPLICATE_LIMIT:
                    return False
            else:
                card_names[card.name()] = 1
        return has_basic or not self.BASIC_REQUIRED

    def __valid_setup(self, to_play:tuple[int], deck:DeckSetup) -> bool:
        indices = set()
        for index in to_play:
            if index in indices:
                return False
            indices.add(index)
            if index < 0 or index >= len(deck.hand) or not deck.hand[index].is_basic():
                return False
        if len(to_play) > 0 and len(to_play) <= deck.BENCH_SIZE + 1:
            return True
        return False

    def __setup(self, to_play:tuple[int], deck:DeckSetup) -> bool:
        if not self.__valid_setup(to_play, deck):
            return False
        for i in range(len(to_play)):
            subtract = 0
            for j in range(i):
                if to_play[j] < to_play[i]:
                    subtract += 1
            assert deck.play_basic(to_play[i]-subtract)
        return True
    
    def team1_setup(self, to_play:tuple[int]):
        self.team1_ready = self.__setup(to_play, self.deck1)

    def team2_setup(self, to_play:tuple[int]):
        self.team2_ready = self.__setup(to_play, self.deck2)
    
    def end_turn(self):
        pass

    def play_from_hand(self):
        pass

    def attack(self):
        pass

    def retreat(self):
        pass
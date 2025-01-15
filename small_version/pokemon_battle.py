from pokemon_card import PokemonCard
from pokemon_types import EnergyType, Condition
import utils

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

    def take_damage(self, amount:int, damage_type:EnergyType) -> 'ActivePokemon':
        total = amount
        if damage_type == self.active_card().get_resistance():
            total -= 20
        if damage_type == self.active_card().get_weakness():
            total += 20
        return ActivePokemon(self.pokemon_cards, self.can_evolve_this_turn, self.damage + total, self.condition, self.energies)
    
    def is_knocked_out(self):
        return self.hp() <= 0

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

    def between_turns(self) -> None:
        for active in self.active:
            active.between_turns()

    def end_turn(self) -> None:
        for i in range(len(self.active)):
            self.active[i] = self.active[i].end_turn()

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
        self.active[active_index] = self.active[active_index].evolve(self.hand[hand_index])
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
        temp = self.active[active_index].retreat(energies)
        self.__discard_energies(energies)
        self.active[active_index] = self.active[0]
        self.active[0] = temp
        return True

    def take_damage(self, amount:int, damage_type:EnergyType) -> None:
        self.active[0] = self.active[0].take_damage(amount, damage_type)
        if self.active[0].is_knocked_out():
            self.discard_from_active()

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

    def attach_energy(self, active_index:int) -> None:
        energy_type = self.next_energies.pop(0)
        self.active[active_index] = self.active[active_index].attach_energy(energy_type)

    def delete_energy(self) -> None:
        self.next_energies.pop(0)

    def play_basic(self, hand_index:int) -> bool:
        """Plays a basic card from the hand to a new spot on the bench

        :param hand_index: The index of the card in the hand
        :type hand_index: int
        :return: True if the card can be placed on the bench, false otherwise
        :rtype: bool
        """
        if self.hand[hand_index].is_basic() and len(self.active) - 1 < self.BENCH_SIZE:
            self.active.append(ActivePokemon((self.hand[hand_index],)))
            self.hand.pop(hand_index)
            return True
        return False

    def replace_starter(self, active_index:int) -> None:
        if active_index > 0:
            self.active[0] = self.active[active_index]
            self.active.pop(active_index)

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

class Turn:

    def __init__(self):
        self.reset()

    def reset(self):
        self.used_supporter = False
        self.retreated = False
        self.energy_used = False

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
        self.next_move_team1 = True

        self.team1_points = 0
        self.team2_points = 0

        self.team1_ready = False
        self.team2_ready = False

        self.turn = Turn()
        self.replace_knocked_out = False

    def team1_move(self) -> bool:
        return self.next_move_team1

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

    def valid_setup(self, to_play:tuple[int], deck:DeckSetup) -> bool:
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

    def __battle_going(self) -> bool:
        return self.team1_ready and self.team2_ready and not self.is_over()

    def __setup(self, to_play:tuple[int], deck:DeckSetup) -> bool:
        if not self.valid_setup(to_play, deck):
            return False
        for i in range(len(to_play)):
            subtract = 0
            for j in range(i):
                if to_play[j] < to_play[i]:
                    subtract += 1
            assert deck.play_basic(to_play[i]-subtract)
        return True
    
    def team1_setup(self, to_play:tuple[int]) -> bool:
        if self.team1_ready:
            return False
        self.team1_ready = self.__setup(to_play, self.deck1)
        if self.team1_ready and self.team2_ready:
            self.start_turn(False)
        return self.team1_ready

    def team2_setup(self, to_play:tuple[int]) -> bool:
        if self.team2_ready:
            return False
        self.team2_ready = self.__setup(to_play, self.deck2)
        if self.team1_ready and self.team2_ready:
            self.start_turn(False)
        return self.team2_ready

    def __verify_basic_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.hand) and deck.hand[index].is_basic()
    
    def __verify_hand_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.hand)
    
    def __verify_active_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.active)

    def __current_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck1
        return self.deck2

    def __defending_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck2
        return self.deck1

    def play_card(self, hand_index:int) -> bool:
        if not self.__battle_going():
            return False
        return False

    def play_basic(self, hand_index:int) -> bool:
        if not self.__battle_going() or self.replace_knocked_out:
            return False
        deck = self.__current_deck()
        valid = self.__verify_basic_index(hand_index, deck)
        if valid:
            return deck.play_basic(hand_index)
        return False

    def evolve(self, hand_index:int, active_index:int) -> bool:
        if not self.__battle_going() or self.replace_knocked_out:
            return False
        deck = self.__current_deck()
        valid1 = self.__verify_hand_index(hand_index, deck)
        valid2 = self.__verify_active_index(active_index, deck)
        if valid1 and valid2:
            if deck.active[active_index].can_evolve(deck.hand[hand_index]):
                deck.evolve(hand_index, active_index)
                return True
        return False

    def retreat(self, active_index:int, energies:list[EnergyType]) -> bool:
        if not self.__could_retreat():
            return False
        deck = self.__current_deck()
        valid = self.__verify_active_index(active_index, deck)
        if valid:
            energy_dict = utils.tuple_to_counts(energies)
            if deck.active[0].can_retreat(energy_dict):
                deck.retreat(active_index, energy_dict)
                return True
        return False

    def attack(self, attack_index:int) -> bool:
        if not self.__battle_going():
            return False
        deck = self.__current_deck()
        if attack_index >= 0 and attack_index < len(deck.active[0].active_card().attacks):
            active_count =   sum(deck.active[0].energies.values())
            required_count = sum(deck.active[0].active_card().attacks[attack_index].energy_cost.values())
            if required_count > active_count:
                return False
            for energy, count in deck.active[0].active_card().attacks[attack_index].energy_cost.items():
                if not energy == EnergyType.COLORLESS and count > deck.active[0].energies[energy]:
                    return False
            self.__defending_deck().take_damage(deck.active[0].active_card().attacks[attack_index].base_damage, deck.active[0].active_card().get_energy_type())
            if self.__defending_deck().active[0].is_knocked_out():
                if self.next_move_team1:
                    self.team1_points += 1 if self.__defending_deck().active[0].active_card().level <= 100 else 2
                else:
                    self.team2_points += 1 if self.__defending_deck().active[0].active_card().level <= 100 else 2
                self.replace_knocked_out = True
                self.next_move_team1 = not self.next_move_team1
            else:
                self.end_turn()
            return True
        return False

    def use_ability(self, ability_index:int) -> bool:
        if not self.__battle_going():
            return False
        return False

    def select(self, index:int) -> bool:
        actions = self.available_actions()
        if 'select' in actions:
            if 'new_active' in actions:
                deck = self.__current_deck()
                if self.__verify_active_index(index, deck):
                    deck.replace_starter(index)
                    return True
        return False

    def place_energy(self, active_index:int) -> bool:
        if not self.__battle_going() and not self.replace_knocked_out:
            return False
        deck = self.__current_deck()
        valid = self.__verify_active_index(active_index, deck)
        if valid:
            if not self.turn.energy_used:
                deck.attach_energy(active_index)
                self.turn.energy_used = True
                return True
        return False

    def between_turns(self) -> None:
        self.deck1.between_turns()
        self.deck2.between_turns()

    def start_turn(self, generate_energy:bool=True) -> None:
        self.__current_deck().start_turn(generate_energy)
        self.turn.energy_used = not generate_energy

    def end_turn(self) -> bool:
        if not self.__battle_going():
            return False
        if not self.turn.energy_used:
            self.__current_deck().delete_energy()
        self.__current_deck().end_turn()
        self.next_move_team1 = not self.next_move_team1
        self.turn_number += 1
        self.turn.reset()
        self.between_turns()
        self.start_turn()
        return True
    
    def __valid_basic_indices(self) -> list[int]:
        deck = self.__current_deck()
        return [i for i in range(len(deck.hand)) if deck.hand[i].is_basic()]
    
    def __could_retreat(self) -> bool:
        deck = self.__current_deck()
        return not self.replace_knocked_out and self.__battle_going() and not self.turn.retreated and \
               sum(deck.active[0].energies.values()) >= deck.active[0].active_card().retreat_cost
    
    def __possible_evolutions(self) -> list[tuple[PokemonCard,ActivePokemon]]:
        if not self.__battle_going() or self.replace_knocked_out:
            return []
        deck = self.__current_deck()
        pairs = []
        for card in deck.hand:
            for active in deck.active:
                if active.can_evolve(card):
                    pairs.append((card,active))
        return pairs

    def __can_attack(self) -> bool:
        if not self.replace_knocked_out and self.__battle_going():
            deck = self.__current_deck()
            for attack_index in range(len(deck.active[0].active_card().attacks)):
                active_count   = sum(deck.active[0].energies.values())
                required_count = sum(deck.active[0].active_card().attacks[attack_index].energy_cost.values())
                if required_count <= active_count:
                    enough = True
                    for energy, cost in deck.active[0].active_card().attacks[attack_index].energy_cost.items():
                        if not energy == EnergyType.COLORLESS and (energy not in deck.active[0].energies or cost > deck.active[0].energies[energy]):
                            enough = False
                    if enough:
                        return True
        return False

    def available_actions(self) -> list[str]:
        if not self.__battle_going():
            if not self.is_over():
                return ['play']
            return []
        if self.replace_knocked_out:
            return ['select', 'new_active']
        moves = []
        if len(self.__valid_basic_indices()) > 0:
            moves.append('play_basic')
        if self.__could_retreat():
            moves.append('retreat')
        if len(self.__possible_evolutions()) > 0:
            moves.append('evolve')
        if self.__can_attack():
            moves.append('attack')
        if not self.turn.energy_used:
            moves.append('place_energy')
        moves.append('end_turn')
        return moves

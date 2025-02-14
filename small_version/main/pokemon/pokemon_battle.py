from pokemon.pokemon_card import PokemonCard, PlayingCard, CardType, Attack, PokemonType
from pokemon.pokemon_types import EnergyType, Condition, EnergyContainer
import pokemon.utils as utils

import random
from dataclasses import dataclass
from collections import deque
from enum import Enum
from frozendict import frozendict
from typing import Any

class ActivePokemon:

    def __init__(self, cards:list[PokemonCard], turns:int=0, damage:int=0, conditions:list[Condition]|None=None, energies:EnergyContainer|None=None):
        self.pokemon_cards = cards
        self.turns_in_active = turns
        self.damage = damage
        self.conditions = conditions if conditions is not None else list[Condition]()
        self.energies = energies if energies is not None else EnergyContainer()
        self.abilities_used = utils.Collection[int]()

    def copy(self) -> 'ActivePokemon':
        return ActivePokemon(list(self.pokemon_cards), self.turns_in_active, self.damage, list(self.conditions), self.energies)

    def active_card(self) -> PokemonCard:
        return self.pokemon_cards[0]

    def evolve(self, card:PokemonCard) -> None:
        self.pokemon_cards.insert(0, card)
        self.conditions.clear()
        self.turns_in_active = 0

    def hp(self) -> int:
        return max(self.active_card().hit_points - self.damage, 0)
    
    def heal(self, amount:int) -> None:
        self.damage -= amount
        self.damage = max(self.damage, 0)

    def end_turn(self) -> None:
        self.turns_in_active += 1
        self.abilities_used = utils.Collection[int]()

    def use_ability(self, ability_index:int) -> None:
        self.abilities_used = self.abilities_used.add_item(ability_index)

    def total_abilities_used(self) -> int:
        return self.abilities_used.size()
    
    def used_ability(self, ability_index:int) -> int:
        return self.abilities_used.size_of(ability_index)

    def between_turns(self) -> None:
        pass

    def attach_energy(self, energy:EnergyType) -> None:
        self.energies = self.energies.add_energy(energy)

    def retreat(self, energies:EnergyContainer) -> None:
        self.energies = self.energies.remove_energies(energies)

    def discard_energy(self, energy_type:EnergyContainer, number:int) -> EnergyContainer:
        if self.energies.size_of(energy_type) > 0:
            remove = min(number, self.energies.size_of(energy_type))
            removed = EnergyContainer(frozendict({energy_type:remove}))
            self.energies = self.energies.remove_energies(removed)
            return removed
        return EnergyContainer()

    def take_damage(self, amount:int, damage_type:EnergyType, apply_weakness_resistance:bool) -> 'ActivePokemon':
        total = amount
        if apply_weakness_resistance:
            if damage_type == self.active_card().get_resistance():
                total -= 20
            if damage_type == self.active_card().get_weakness():
                total += 20
        self.damage += total
    
    def is_knocked_out(self):
        return self.hp() <= 0

    def get_energies(self) -> EnergyContainer:
        return self.energies

    def get_cards(self) -> list[PokemonCard]:
        return list(self.pokemon_cards)

@dataclass(frozen=True)
class Deck:
    name:str
    cards:tuple[PlayingCard]
    energies:tuple[EnergyType]
    
    def get_cards(self) -> tuple[PlayingCard]:
        """Get a list of the cards used in the deck

        :return: The cards in the deck
        :rtype: list[PlayingCard]
        """
        return self.cards

class DeckSetup:

    def __init__(self, deck:Deck, initial_hand_size:int, initial_energies:int, shuffle:bool=True,*, active:list[ActivePokemon]|None=None, discard:list[PlayingCard]|None=None, energy_discard:EnergyContainer|None=None):
        self.energies = list(deck.energies)
        cards = list(deck.cards)
        if shuffle:
            cards = self.__shuffle_deck_to_start(cards)
        self.deck = deque(cards[initial_hand_size:])
        self.hand = cards[0:initial_hand_size]
        self.active = active if active is not None else list[ActivePokemon]()
        self.discard = discard if discard is not None else list[PlayingCard]()
        self.energy_discard = energy_discard if discard is not None else EnergyContainer()
        self.next_energies = deque([self.__decide_next_energy() for _ in range(initial_energies)])

    def __shuffle_deck_to_start(self, cards:list[PlayingCard]) -> list[PlayingCard]:
        basics = [card for card in cards if card.is_basic()]
        starter = random.choice(basics)
        cards.remove(starter)
        random.shuffle(cards)
        cards.insert(0,starter)
        return cards

    def __decide_next_energy(self) -> EnergyType:
        return random.choice(self.energies)

    def bench(self) -> list[PlayingCard]:
        return self.active[1:]
    
    def bench_size(self) -> int:
        return len(self.active) - 1

    def start_turn(self, get_energy:bool=True, draw_card:bool=True) -> None:
        if get_energy:
            self.next_energies.append(self.__decide_next_energy())
        if draw_card:
            self.draw_card()

    def draw_card(self) -> None: 
        card = self.deck.popleft()
        self.hand.append(card)

    def draw_basic(self) -> None:
        basics = [card for card in self.deck if card.is_basic()]
        if len(basics) > 0:
            basic = random.choice(basics)
            self.deck.remove(basic)
            self.hand.append(basic)
        deck = list(self.deck)
        random.shuffle(deck)
        self.deck = deque(deck)

    def get_cards(self, how_many:int, card_type:CardType, energy_type:EnergyType, is_basic:bool) -> None:
        matches = [card for card in self.deck if (card.get_card_type()==card_type and (not card_type==CardType.POKEMON or energy_type is None or card.get_energy_type()==energy_type) and (not is_basic or card.is_basic()))]
        how_many = min(how_many, len(matches))
        if how_many > 0:
            random.shuffle(matches)
            to_hand = matches[:how_many]
            deck = list(self.deck)
            for card in to_hand:
                deck.remove(card)
            self.hand.extend(to_hand)
            random.shuffle(deck)
            self.deck = deque(deck)
        else:
            deck = list(self.deck)
            random.shuffle(deck)
            self.deck = deque(deck)

    def between_turns(self) -> None:
        for active in self.active:
            active.between_turns()

    def end_turn(self) -> None:
        for active in self.active:
            active.end_turn()

    def play_card_from_hand(self, hand_index:int) -> None:
        card = self.hand.pop(hand_index)
        self.discard.append(card)

    def evolve(self, hand_index:int, active_index:int) -> None:
        card = self.hand.pop(hand_index)
        self.active[active_index].evolve(card)

    def retreat(self, active_index:int, energies:EnergyContainer) -> None:
        if active_index == 0:
            return
        to_bench = self.active[0]
        to_bench.retreat(energies)
        self.energy_discard = self.energy_discard.add_energies(energies)
        self.active[0] = self.active[active_index]
        self.active[active_index] = to_bench

    def take_damage(self, amount:int, damage_type:EnergyType, *, active_index:int=0, apply_weakness_resistance:bool=True) -> None:
        self.active[active_index].take_damage(amount, damage_type, apply_weakness_resistance)
        if self.active[active_index].is_knocked_out():
            self.discard_from_active(active_index)

    def shuffle_hand_into_deck(self) -> None:
        cards = list(self.hand)
        self.hand.clear()
        while len(self.deck) > 0:
            cards.append(self.deck.popleft())
        random.shuffle(cards)
        self.deck = deque(cards)

    def discard_from_active(self, active_index:int) -> None:
        self.discard.extend(self.active[active_index].get_cards())
        energies = self.active[active_index].get_energies()
        self.energy_discard = self.energy_discard.add_energies(energies)
        if active_index == 0:
            self.active[active_index] = None
        else:
            self.active.pop(active_index)

    def attach_energy(self, active_index:int) -> None:
        energy_type = self.next_energies.popleft()
        self.active[active_index].attach_energy(energy_type)

    def delete_energy(self) -> None:
        self.next_energies.popleft()

    def play_basic(self, hand_index:int) -> None:
        card = self.hand.pop(hand_index)
        self.active.append(ActivePokemon([card]))

    def set_starter(self, active_index:int) -> None:
        if active_index > 0:
            card = self.active[0]
            self.active[0] = self.active[active_index]
            if card is not None:
                self.active[active_index] = card
            else:
                self.active.pop(active_index)

@dataclass
class OpponentDeckView:
    active:         list[ActivePokemon]
    hand_size:      int
    deck_size:      int
    energy_queue:   deque[EnergyType]
    discard_pile:   list[PlayingCard]
    energy_discard: EnergyContainer

@dataclass
class OwnDeckView:
    active:         list[ActivePokemon]
    hand:           list[PlayingCard]
    deck_size:      int
    energy_queue:   deque[EnergyType]
    discard_pile:   list[PlayingCard]
    energy_discard: EnergyContainer

def get_opponent_deck_view(deck:DeckSetup) -> OpponentDeckView:
    """Get a view of a DeckSetup without the ability to change the DeckSetup

    :param deck: The deck to view
    :type deck: DeckSetup
    :return: The immutable partial view of the deck
    :rtype: DeckView
    """
    active = list[ActivePokemon]()
    for a in deck.active:
        if a is not None:
            active.append(a.copy())
        else:
            active.append(None)
    return OpponentDeckView(active, len(deck.hand), len(deck.deck), list(deck.next_energies), list(deck.discard), deck.energy_discard)

def get_own_deck_view(deck:DeckSetup) -> OpponentDeckView:
    """Get a view of a DeckSetup without the ability to change the DeckSetup

    :param deck: The deck to view
    :type deck: DeckSetup
    :return: The immutable partial view of the deck
    :rtype: DeckView
    """
    active = list[ActivePokemon]()
    for a in deck.active:
        if a is not None:
            active.append(a.copy())
        else:
            active.append(None)
    return OwnDeckView(active, list(deck.hand), len(deck.deck), list(deck.next_energies), list(deck.discard), deck.energy_discard)

class Turn:

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.used_supporters = 0
        self.retreats        = 0
        self.energy_used     = False
        self.attacks_used    = 0

@dataclass(frozen=True)
class Rules:
    actions           :set['Action']
    effects           :set['Effect']
    damage_effects    :set['DamageEffect']
    DECK_SIZE         :int  = 20
    DUPLICATE_LIMIT   :int  = 2
    BASIC_REQUIRED    :bool = True
    POINTS_TO         :int  = 3
    TURNS_TO_EVOLVE   :int  = 1
    BENCH_SIZE        :int  = 3
    INITIAL_HAND_SIZE :int  = 5
    MAX_HAND_SIZE     :int  = 10
    FUTURE_ENERGIES   :int  = 1
    SHUFFLE           :bool = True
    SUPPORTERS_PER_TURN:int = 1
    ATTACKS_PER_TURN  :int  = 1
    ABILITIES_PER_CARD:int  = 1
    RETREATS_PER_TURN :int  = 1

    def get_actions(self) -> dict[str,'Action']:
        return {action.action_name():action for action in self.actions}

    def get_effects(self) -> dict[str,'Effect']:
        return {effect.effect_name():effect for effect in self.effects}
    
    def get_damage_effects(self) -> dict[str, 'DamageEffect']:
        return {effect.effect_name():effect for effect in self.damage_effects}

    def is_valid_deck(self, deck:Deck) -> bool:
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
            if card.get_name() in card_names:
                card_names[card.get_name()] += 1
                if card_names[card.get_name()] > self.DUPLICATE_LIMIT:
                    return False
            else:
                card_names[card.get_name()] = 1
        return has_basic or not self.BASIC_REQUIRED

class UserInput:
    def __init__(self, input_type:str, prompt:str):
        self.input_type = input_type
        self.prompt = prompt
        self.value = None
        self.has_value = False

    def pass_value(self, value) -> None:
        self.value = value
        self.has_value = True

    def take_value(self) -> Any:
        val = self.value
        self.value = None
        self.has_value = False
        return val

class ActionPriority(Enum):
    NOW            = -1
    ATTACK_EFFECT  = 0
    REPLACE_ACTIVE = 1
    AFTER_REPLACE  = 2
    LATE_EFFECT    = 3
    RETALIATION    = 4
    END_TURN       = 5

class BattleState:

    def __init__(self, deck1:Deck, deck2:Deck, rules:Rules|None, *, turn_number:int=0, next_move_team1:bool=True, team1_points:int=0, team2_points:int=0, team1_ready:bool=False, team2_ready:bool=False, current_turn:Turn|None=None, action_queue:utils.PriorityQueue[tuple[str,tuple]]|None=None):
        self.rules = rules if rules is not None else Rules()
        assert rules.is_valid_deck(deck1)
        assert rules.is_valid_deck(deck2)
        self.deck1 = DeckSetup(deck1, rules.INITIAL_HAND_SIZE, rules.FUTURE_ENERGIES, rules.SHUFFLE)
        self.deck2 = DeckSetup(deck2, rules.INITIAL_HAND_SIZE, rules.FUTURE_ENERGIES, rules.SHUFFLE)
        self.turn_number = turn_number
        self.next_move_team1 = next_move_team1
        self.team1_points = team1_points
        self.team2_points = team2_points
        self.team1_ready = team1_ready
        self.team2_ready = team2_ready
        self.current_turn = current_turn if current_turn is not None else Turn()
        self.action_queue = action_queue if action_queue is not None else utils.PriorityQueue[tuple[str,tuple]]()

    def next_action(self) -> str:
        if self.action_queue.size() > 0:
            return self.action_queue.top()[0]
        return None
    
    def push_action(self, action:tuple[str,tuple], priority:int) -> None:
        if self.battle_going():
            self.action_queue.push(priority, action)

    def get_partial_inputs(self) -> tuple:
        if self.action_queue.size() > 0:
            return self.action_queue.top()[1]

    def top_action(self) -> tuple[str,tuple]:
        if self.battle_going():
            current_action = self.action_queue.top()
            return current_action
    
    def end_current_action(self) -> None:
        if self.action_queue.size() > 0:
            self.action_queue.pop()
    
    def queued_actions(self) -> int:
        return self.action_queue.size()
    
    def end(self) -> None:
        if self.is_over():
            self.action_queue.clear()

    def team1_move(self) -> bool:
        return self.next_move_team1
    
    def team1_turn(self) -> bool:
        return self.turn_number % 2 == 0
    
    def current_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck1
        return self.deck2
    
    def defending_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck2
        return self.deck1
    
    def need_to_replace_active(self) -> bool:
        return len(self.deck1.active) > 0 and self.deck1.active[0] is None or \
               len(self.deck2.active) > 0 and self.deck2.active[0] is None

    def is_over(self) -> bool:
        return self.team1_points >= self.rules.POINTS_TO or self.team2_points >= self.rules.POINTS_TO or \
                (len(self.deck1.active) > 0 and self.deck1.active[0] is None and self.deck1.bench_size() == 0) or \
                (len(self.deck2.active) > 0 and self.deck2.active[0] is None and self.deck2.bench_size() == 0)
    
    def battle_going(self) -> bool:
        return self.team1_ready and self.team2_ready and not self.is_over()
    
    def is_valid_basic_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.hand) and deck.hand[index].is_basic()
    
    def is_valid_trainer_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.hand) and deck.hand[index].is_trainer()
    
    def is_valid_hand_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.hand)
    
    def is_valid_active_index(self, index:int, deck:DeckSetup) -> bool:
        return index >= 0 and index < len(deck.active)
    
    def is_valid_bench_index(self, index:int, deck:DeckSetup) -> bool:
        return index > 0 and index < len(deck.active)
    
    def start_turn(self, generate_energy:bool=True) -> None:
        deck = self.current_deck()
        draw_card = len(deck.deck) > 0 and len(deck.hand) < self.rules.MAX_HAND_SIZE
        deck.start_turn(generate_energy, draw_card)
        self.current_turn.energy_used = not generate_energy

    def end_turn(self) -> bool:
        if self.battle_going():
            if not self.current_turn.energy_used:
                self.current_deck().delete_energy()
            self.current_deck().end_turn()
            self.turn_number += 1
            self.current_turn.reset()
            self.next_move_team1 = self.team1_turn()
            self.between_turns()
            self.start_turn()
            return True
        return False
    
    def between_turns(self) -> None:
        self.deck1.between_turns()
        self.deck2.between_turns()

    def ready_for_action(self, action:str) -> bool:
        return self.battle_going() and (self.queued_actions() == 0 or self.next_action() == action)


class Effect:
    def effect_name(self) -> str:
        pass

    def effect_description(self) -> str:
        pass

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        pass

    def effect(self, battle:BattleState, inputs:tuple) -> bool:
        pass

class DrawCardsEffect(Effect):
    def effect_name(self) -> str:
        return "draw"

    def effect_description(self) -> str:
        return "Draws cards from the deck to the hand"

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.effect_name()):
            if len(inputs) == 1:
                try:
                    n = int(inputs[0])
                except ValueError:
                    return False
                return len(battle.current_deck().deck) > 0
        return False

    def effect(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            n = inputs[0]
            deck = battle.current_deck()
            i = 0
            while i < n and len(deck.deck) > 0 and len(deck.hand) < battle.rules.MAX_HAND_SIZE:
                deck.draw_card()
                i += 1
            return True
        return False

class SwitchMoveEffect(Effect):
    def effect_name(self) -> str:
        return "switch_move"

    def effect_description(self) -> str:
        return "Switch the move from one player to another"

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.effect_name()):
            return battle.next_action() == self.effect_name()
        return False

    def effect(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            battle.next_move_team1 = not battle.next_move_team1
            return True
        return False
    
class EndTurnEffect(Effect):
    def effect_name(self) -> str:
        return "end_turn_effect"

    def effect_description(self) -> str:
        return "End the player's turn"

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.effect_name()):
            return battle.next_action() == self.effect_name() and len(inputs) == 0
        return False

    def effect(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            return battle.end_turn()
        return False

class SwapActiveEffect(Effect):
    def effect_name(self) -> str:
        return "swap_active"

    def effect_description(self) -> str:
        return "Switch the defending pokemon with a benched pokemon"

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        if battle.ready_for_action(self.effect_name()):
            return battle.defending_deck().bench_size() > 0 and len(inputs) == 0
        return False

    def effect(self, battle:BattleState, inputs:tuple) -> bool:
        battle.next_move_team1 = not battle.next_move_team1
        battle.push_action(("select_active", tuple()), ActionPriority.LATE_EFFECT.value)
        battle.push_action(("switch_move", tuple()), ActionPriority.LATE_EFFECT.value)
        return True

class DamageEffect(Effect):
    def effect_name(self) -> str:
        return 'damage'

    def effect_description(self) -> str:
        return "Damage an ActivePokemon"

    def is_valid(self, battle:BattleState, inputs:tuple[str|int,int]) -> bool:
        if battle.ready_for_action(self.effect_name()):
            if len(inputs) == 2 and inputs[1] > 0:
                if inputs[0] in {'all', 'bench'} or isinstance(inputs[0], UserInput):
                    return True
                else:
                    try:
                        active_index = int(inputs[0])
                    except ValueError:
                        return False
                    if battle.is_valid_active_index(active_index, battle.current_deck()):
                        return True
        return False

    def effect(self, battle:BattleState, inputs:tuple[str|int,int]) -> bool:
        if self.is_valid(battle, inputs):
            who, how_much = inputs
            if who == 'all':
                for active in battle.current_deck().active:
                    active.take_damage(how_much, EnergyType.COLORLESS, False)
            elif who == 'bench':
                for active in battle.current_deck().active[1:]:
                    active.take_damage(how_much, EnergyType.COLORLESS, False)
            else:
                who = int(who)
                battle.current_deck().active[who].take_damage(how_much, EnergyType.COLORLESS, False)
            return True
        return False

class HealEffect(Effect):
    def effect_name(self) -> str:
        return 'heal'

    def effect_description(self) -> str:
        return "Heal an ActivePokemon's health"

    def is_valid(self, battle:BattleState, inputs:tuple[str|int,int]) -> bool:
        if battle.ready_for_action(self.effect_name()):
            if len(inputs) == 2 and inputs[1] > 0:
                if inputs[0] in {'all'} or isinstance(inputs[0], UserInput):
                    for active in battle.current_deck().active:
                        if active.damage > 0:
                            return True
                elif inputs[0] == 'bench':
                    for active in battle.current_deck().active[1:]:
                        if active.damage > 0:
                            return True
                else:
                    try:
                        active_index = int(inputs[0])
                    except ValueError:
                        return False
                    if battle.is_valid_active_index(active_index, battle.current_deck()):
                        return battle.current_deck().active[active_index].damage > 0
        return False

    def effect(self, battle:BattleState, inputs:tuple[str|int,int]) -> bool:
        if self.is_valid(battle, inputs):
            who, how_much = inputs
            if who == 'all':
                for active in battle.current_deck().active:
                    active.heal(how_much)
            elif who == 'bench':
                for active in battle.current_deck().active[1:]:
                    active.heal(how_much)
            else:
                who = int(who)
                battle.current_deck().active[who].heal(how_much)
            return True
        return False
    
class DiscardEnergyEffect(Effect):
    def effect_name(self) -> str:
        return 'discard_energy'

    def effect_description(self) -> str:
        return "Discard energy attached to a pokemon"

    def is_valid(self, battle:BattleState, inputs:tuple[bool,str|int,int,int]) -> bool:
        if battle.ready_for_action(self.effect_name()):
            if len(inputs) == 4:
                which_deck, who, how_many, what_type = inputs
                if how_many > 0:
                    deck = battle.current_deck() if which_deck else battle.defending_deck()
                    if who == 'random':
                        return True
                    else:
                        try:
                            who = int(who)
                        except ValueError:
                            return False
                        return battle.is_valid_active_index(who, deck)
        return False

    def effect(self, battle:BattleState, inputs:tuple[str|int,int]) -> bool:
        if self.is_valid(battle, inputs):
            which_deck, who, how_many, what_type = inputs
            deck = battle.current_deck() if which_deck else battle.defending_deck()
            if who == 'random':
                print("do this")
            else:
                who = int(who)
                removed = deck.active[who].discard_energy(what_type, how_many)
                deck.energy_discard.add_energy(removed)
            return True
        return False

class GetCardEffect(Effect):
    def effect_name(self) -> str:
        return "get_card"

    def effect_description(self) -> str:
        return "Find a card or cards in the deck and place them in the hand."

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        if battle.ready_for_action(self.effect_name()):
            if len(inputs) == 4:
                how_many, card_type, energy_type, is_basic = inputs
                deck = battle.current_deck()
                how_many = min(how_many, battle.rules.MAX_HAND_SIZE-len(deck.hand), len(deck.deck))
                if how_many > 0:
                    return True
        return False

    def effect(self, battle:BattleState, inputs:tuple) -> bool:
        if self.is_valid(battle, inputs):
            how_many, card_type, energy_type, is_basic = inputs
            deck = battle.current_deck()
            how_many = min(how_many, battle.rules.MAX_HAND_SIZE-len(deck.hand), len(deck.deck))
            deck.get_cards(how_many, card_type, energy_type, is_basic)
            return True
        return False


class DamageEffect:
    def effect_name(self) -> str:
        pass

    def effect_description(self) -> str:
        pass

    def damage(self, battle:BattleState, attacker:ActivePokemon, attack:Attack, inputs:tuple[int,]) -> bool:
        pass

class BaseDamageEffect(DamageEffect):
    def effect_name(self) -> str:
        return 'base'

    def effect_description(self) -> str:
        return 'Base damage'

    def damage(self, battle:BattleState, attacker:ActivePokemon, attack:Attack, inputs:tuple[int]) -> bool:
        return inputs[0]
    
class EnergyBoostDamageEffect(DamageEffect):
    def effect_name(self) -> str:
        return 'energy_boost'

    def effect_description(self) -> str:
        return 'Does more damage if this card has more energies attached to it'

    def damage(self, battle:BattleState, attacker:ActivePokemon, attack:Attack, inputs:tuple[int]) -> bool:
        base, boost, extra_needed, type_needed = inputs
        if type_needed == EnergyType.COLORLESS:
            return base + (boost if attacker.energies.size() >= extra_needed + attack.energy_cost.size() else 0)
        else:
            if attacker.energies.size_of(type_needed) >= extra_needed + attack.energy_cost.size_of(type_needed) \
               and attacker.energies.size() >= extra_needed + attack.energy_cost.size():
                return base + boost
            return base


class Action:

    def action(self, battle:BattleState, inputs:tuple) -> bool:
        pass

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        pass

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        pass

    def could_act(self, battle:BattleState) -> bool:
        pass

    def action_name(self) -> str:
        pass

    def action_description(self) -> str:
        pass

    def input_format(self) -> str:
        pass

class PlayTrainerAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            hand_index = inputs[0]
            deck = battle.current_deck()
            trainer = deck.hand[hand_index]
            deck.play_card_from_hand(hand_index)
            battle.push_action(trainer.get_action(), ActionPriority.ATTACK_EFFECT.value)
            if trainer.get_card_type() == CardType.SUPPORTER:
                battle.current_turn.used_supporters += 1
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            hand_index = inputs[0]
            deck = battle.current_deck()
            if battle.is_valid_trainer_index(hand_index, deck):
                if not deck.hand[hand_index].get_card_type() == CardType.SUPPORTER or battle.current_turn.used_supporters < battle.rules.SUPPORTERS_PER_TURN:
                    effect, inputs = deck.hand[hand_index].get_action()
                    if effect in battle.rules.get_effects():
                        return battle.rules.get_effects()[effect].is_valid(battle, inputs)
        return False

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                hand_index = int(inputs[0])
            except ValueError:
                return False, None
            return True, (hand_index,)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        for i in range(len(deck.hand)):
            if self.is_valid(battle, (i,)):
                return True
        return False

    def action_name(self) -> str:
        return "trainer"

    def action_description(self) -> str:
        return "Play a trainer card from your hand"

    def input_format(self) -> str:
        return "trainer x"

class SetupAction(Action):
    def action(self, battle:BattleState, inputs:tuple[bool, int]) -> bool:
        if not self.is_valid(battle, inputs):
            return False
        is_team1 = inputs[0]
        for i in range(1,len(inputs)):
            subtract = 0
            for j in range(1,i):
                if inputs[j] < inputs[i]:
                    subtract += 1
            if is_team1:
                battle.deck1.play_basic(inputs[i]-subtract)
            else:
                battle.deck2.play_basic(inputs[i]-subtract)
        if is_team1:
            battle.team1_ready = True
        else:
            battle.team2_ready = True
        if battle.team1_ready and battle.team2_ready:
            battle.start_turn(False)
        return True
    
    def is_valid(self, battle:BattleState, inputs:tuple[bool,int]) -> bool:
        is_team1 = inputs[0]
        if not battle.team1_ready and is_team1 or not battle.team2_ready and not is_team1:
            basic_indices = inputs[1:]
            indices = set()
            for index in basic_indices:
                if index in indices:
                    return False
                indices.add(index)
                if not battle.is_valid_basic_index(index, battle.deck1 if is_team1 else battle.deck2):
                    return False
            if len(inputs) > 0 and len(inputs) <= battle.rules.BENCH_SIZE + 1:
                return True
        return False
    
    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool,tuple]:
        indices = []
        for index in inputs:
            try:
                indices.append(int(index))
            except ValueError:
                return False, None
        return True, tuple(indices)
    
    def could_act(self, battle:BattleState) -> bool:
        return not battle.team1_ready or not battle.team2_ready
    
    def action_name(self) -> str:
        return "setup"
    
    def action_description(self) -> str:
        return "Pick a starter and any bench pokemon to start"
    
    def input_format(self) -> str:
        return "setup x1 ... xn"

class PlayBasicAction(Action):

    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            hand_index = inputs[0]
            deck = battle.current_deck()
            deck.play_basic(hand_index)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            hand_index = inputs[0]
            deck = battle.current_deck()
            return battle.is_valid_basic_index(hand_index, deck) and deck.bench_size() < battle.rules.BENCH_SIZE
        return False

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                hand_index = int(inputs[0])
            except ValueError:
                return False, None
            return True, (hand_index,)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        for hand_index in range(len(deck.hand)):
            if self.is_valid(battle, (hand_index,)):
                return True
        return False

    def action_name(self) -> str:
        return "play_basic"

    def action_description(self) -> str:
        return "Place a basic from the hand to the bench"
    
    def input_format(self) -> str:
        return "play_basic x"

class EvolveAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            hand_index, active_index = inputs
            deck = battle.current_deck()
            deck.evolve(hand_index, active_index)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int,int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            hand_index, active_index = inputs
            deck = battle.current_deck()
            valid1 = battle.is_valid_hand_index(hand_index, deck)
            valid2 = battle.is_valid_active_index(active_index, deck)
            if valid1 and valid2 and deck.hand[hand_index].is_pokemon():
                if deck.active[active_index].turns_in_active >= battle.rules.TURNS_TO_EVOLVE and \
                deck.hand[hand_index].evolves_from() == deck.active[active_index].active_card().pokemon:
                    return True
        return False

    def is_valid_raw(self, inputs:tuple) -> tuple[bool, tuple]:
        if len(inputs) == 2:
            try:
                hand_index =   int(inputs[0])
                active_index = int(inputs[1])
            except ValueError:
                return False, None
            return True, (hand_index, active_index)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        for hand_index in range(len(deck.hand)):
            for active_index in range(len(deck.active)):
                if self.is_valid(battle, (hand_index, active_index)):
                    return True
        return False

    def action_name(self) -> str:
        return "evolve"

    def action_description(self) -> str:
        return "Play a card from the hand to evolve an active pokemon"
    
    def input_format(self) -> str:
        return "evolve x y"

class AbilityAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int,int]) -> bool:
        if self.is_valid(battle, inputs):
            active_index, ability_index = inputs
            deck = battle.current_deck()
            ability = deck.active[active_index].active_card().abilities[ability_index]
            effect, effect_inputs = ability.get_effect()
            battle.rules.get_effects()[effect].effect(battle, effect_inputs)
            deck.active[active_index].use_ability(ability_index)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int,int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            active_index, ability_index = inputs
            deck = battle.current_deck()
            if battle.is_valid_active_index(active_index, deck):
                abilities = deck.active[active_index].active_card().abilities
                if len(abilities) > 0 and ability_index >= 0 and ability_index < len(abilities):
                    if deck.active[active_index].used_ability(ability_index) < battle.rules.ABILITIES_PER_CARD:
                        ability = abilities[ability_index]
                        if ability.trigger == 'user':
                            effect, effect_inputs = ability.get_effect()
                            if effect in battle.rules.get_effects():
                                return battle.rules.get_effects()[effect].is_valid(battle, effect_inputs)
        return False

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        if len(inputs) == 2:
            try:
                active_index = int(inputs[0])
                ability_index = int(inputs[1])
            except ValueError:
                return False, "ability requires two ints"
            return True, (active_index, ability_index)
        return False, "ability requires 2 inputs"

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        for i in range(len(deck.active)):
            if deck.active[i] is not None:
                for j in range(len(deck.active[i].active_card().abilities)):
                    if self.is_valid(battle, (i,j)):
                        return True
        return False

    def action_name(self) -> str:
        return 'ability'

    def action_description(self) -> str:
        return "Use a pokemon's ability"

    def input_format(self) -> str:
        return 'ability x y'

class AttackAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            attack_index = inputs[0]
            deck = battle.current_deck()
            defending_deck = battle.defending_deck()
            attacker = deck.active[0]
            attack = attacker.active_card().attacks[attack_index]
            attacked = defending_deck.active[0].active_card()
            damage_effect, damage_inputs = attack.get_damage_effect()
            if damage_effect in battle.rules.get_damage_effects():
                damage = battle.rules.get_damage_effects()[damage_effect].damage(battle, attacker, attack, damage_inputs)
            else:
                damage = battle.rules.get_damage_effects()['base'].damage(battle, damage_inputs)
            defending_deck.take_damage(damage, deck.active[0].active_card().get_energy_type())
            if attack.get_effect() is not None:
                attack_effect, attack_inputs = attack.get_effect()
                if attack_effect in battle.rules.get_effects():
                    if battle.rules.get_effects()[attack_effect].is_valid(battle, attack_inputs):
                        battle.push_action(attack.get_effect(), ActionPriority.ATTACK_EFFECT.value)
            battle.current_turn.attacks_used += 1
            if defending_deck.active[0] is None:
                if battle.team1_turn():
                    battle.team1_points += 1 if attacked.level <= 100 else 2
                else:
                    battle.team2_points += 1 if attacked.level <= 100 else 2
                if not battle.is_over():
                    battle.push_action(('switch_move', tuple()), ActionPriority.REPLACE_ACTIVE.value)
                    battle.push_action(('select_active', tuple()), ActionPriority.REPLACE_ACTIVE.value)
                    battle.push_action(('switch_move', tuple()), ActionPriority.REPLACE_ACTIVE.value)
                else:
                    battle.end()
            if battle.current_turn.attacks_used >= battle.rules.ATTACKS_PER_TURN:
                battle.push_action(('end_turn_effect', tuple()), ActionPriority.END_TURN.value)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            deck = battle.current_deck()
            attack_index = inputs[0]
            if attack_index >= 0 and attack_index < len(deck.active[0].active_card().attacks) and battle.current_turn.attacks_used < battle.rules.ATTACKS_PER_TURN:
                return deck.active[0].energies.at_least_as_big(deck.active[0].active_card().attacks[attack_index].energy_cost)
        return False

    def is_valid_raw(self, inputs:tuple) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                attack_index = int(inputs[0])
            except ValueError:
                return False, None
            return True, (attack_index,)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        if len(deck.active) > 0 and deck.active[0] is not None:
            for attack_index in range(len(deck.active[0].active_card().attacks)):
                if self.is_valid(battle, (attack_index,)):
                    return True
        return False

    def action_name(self) -> str:
        return "attack"

    def action_description(self) -> str:
        return "Use an attack"
    
    def input_format(self) -> str:
        return "attack x"

class RetreatAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int, EnergyContainer]) -> bool:
        if self.is_valid(battle, inputs):
            active_index, energies = inputs
            deck = battle.current_deck()
            deck.retreat(active_index, energies)
            battle.current_turn.retreats += 1
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int, EnergyContainer]) -> bool:
        if battle.ready_for_action(self.action_name()):
            active_index, energies = inputs
            deck = battle.current_deck()
            if battle.is_valid_active_index(active_index, deck):
                if battle.current_turn.retreats < battle.rules.RETREATS_PER_TURN:
                    if deck.bench_size() > 0 and deck.active[0].active_card().retreat_cost == energies.size() and deck.active[0].energies.at_least_as_big(energies):
                        return True
        return False

    def is_valid_raw(self, inputs:tuple[str,...]) -> tuple[bool, tuple]:
        if len(inputs) >= 1:
            try:
                active_index = int(inputs[0])
            except ValueError:
                return False, None
            energies = EnergyContainer()
            for token in inputs[1:]:
                try:
                    energies = energies.add_energy(EnergyType[token.upper()])
                except KeyError:
                    return False, None
            return True, (active_index, energies)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        if battle.battle_going() and battle.ready_for_action(self.action_name()):
            deck = battle.current_deck()
            if battle.current_turn.retreats < battle.rules.RETREATS_PER_TURN:
                return deck.active[0].active_card().retreat_cost <= deck.active[0].energies.size() and deck.bench_size() > 0
        return False

    def action_name(self) -> str:
        return "retreat"

    def action_description(self) -> str:
        return "Swap the active pokemon for a bench pokemon"
    
    def input_format(self) -> str:
        return "retreat x e1 ... en"

class PlaceEnergyAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            active_index = inputs[0]
            deck = battle.current_deck()
            deck.attach_energy(active_index)
            battle.current_turn.energy_used = True
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            active_index = inputs[0]
            deck = battle.current_deck()
            return battle.is_valid_active_index(active_index, deck) and not battle.current_turn.energy_used
        return False

    def is_valid_raw(self, inputs:tuple[int]) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                active_index = int(inputs[0])
            except ValueError:
                return False, None
            return True, (active_index,)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        for i in range(len(deck.active)):
            if self.is_valid(battle, (i,)):
                return True
        return False

    def action_name(self) -> str:
        return "place_energy"

    def action_description(self) -> str:
        return "Place an energy on one of the active pokemon"
    
    def input_format(self) -> str:
        return "place_energy x"

class SelectActiveAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            bench_index = inputs[0]
            deck = battle.current_deck()
            deck.set_starter(bench_index)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if battle.ready_for_action(self.action_name()):
            bench_index = inputs[0]
            deck = battle.current_deck()
            return battle.next_action() == self.action_name() and battle.is_valid_bench_index(bench_index, deck)
        return False

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                index = int(inputs[0])
            except ValueError:
                return False, None
            return True, (index,)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        deck = battle.current_deck()
        for i in range(1, len(deck.active)):
            if self.is_valid(battle, (i,)):
                return True
        return False

    def action_name(self) -> str:
        return "select_active"

    def action_description(self) -> str:
        return "Select a new active pokemon"
    
    def input_format(self) -> str:
        return "select_active x"

class SelectAction(Action):
    def action(self, battle:BattleState, inputs:tuple[UserInput,str]) -> bool:
        if self.is_valid(battle, inputs):
            user_input, val = inputs
            user_input.pass_value(val)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[UserInput,str]) -> bool:
        if battle.ready_for_action(self.action_name()):
            return battle.next_action() == self.action_name() and len(inputs) == 2

    def is_valid_raw(self, inputs:tuple[UserInput, str]) -> tuple[bool, tuple]:
        if len(inputs) == 2:
            user_input, val = inputs
            return True, (user_input,val)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        if battle.ready_for_action(self.action_name()):
            return battle.next_action() == self.action_name()

    def action_name(self) -> str:
        return 'select'

    def action_description(self) -> str:
        return 'Select a value as part of an attack/trainer/ability'

    def input_format(self) -> str:
        return 'select x'

class EndTurnAction(Action):
    def action(self, battle:BattleState, inputs:tuple) -> bool:
        if self.is_valid(battle, inputs):
            battle.end_turn()
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        return battle.ready_for_action(self.action_name()) and len(inputs) == 0

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        return len(inputs) == 0, inputs

    def could_act(self, battle:BattleState) -> bool:
        return self.is_valid(battle, tuple())

    def action_name(self) -> str:
        return "end_turn"

    def action_description(self) -> str:
        return "End the turn"
    
    def input_format(self) -> str:
        return "end_turn"


class Battle:
    """Represents a battle between two decks of cards
    """

    def __init__(self, state:BattleState):
        self.state = state
        self.log = None # TODO

    def team1_move(self) -> bool:
        return self.state.team1_move()
    
    def team1_turn(self) -> bool:
        return self.state.team1_turn()

    def is_over(self) -> bool:
        return self.state.is_over()
    
    def action(self, action:str, inputs:tuple) -> bool:
        success = True
        if action in self.state.rules.get_actions():
            success = self.state.rules.get_actions()[action].action(self.state, inputs)
            if not success:
                return False
            if action == self.state.next_action():
                self.state.end_current_action()
        while self.state.queued_actions() > 0:
            sub_action, sub_inputs = self.state.top_action()
            if sub_action in self.state.rules.get_actions():
                return True
            
            user_input_needed = False
            for sub_input in sub_inputs:
                if isinstance(sub_input, UserInput) and not sub_input.has_value:
                    self.state.push_action(('select', (sub_input,)), ActionPriority.NOW.value)
                    user_input_needed = True
            if user_input_needed:
                return success
            
            if sub_action in self.state.rules.get_effects():
                new_inputs = []
                for i in range(len(sub_inputs)):
                    sub_input = sub_inputs[i]
                    if isinstance(sub_input, UserInput):
                        new_inputs.append(sub_input.take_value())
                    else:
                        new_inputs.append(sub_input)
                if self.state.rules.get_effects()[sub_action].effect(self.state, tuple(new_inputs)):
                    self.state.end_current_action()
                else:
                    success = False
            else:
                print(f"error: {sub_action}: {sub_inputs}")
        return success
    
    def available_actions(self) -> dict[str,Action]:
        return {name:action for name,action in self.state.rules.get_actions().items() if action.could_act(self.state)}

    def get_rules(self) -> Rules:
        return self.state.rules
    
    def get_score(self) -> tuple[int]:
        return self.state.team1_points, self.state.team2_points
    
    def get_partial_inputs(self) -> tuple:
        return self.state.get_partial_inputs()

def standard_actions() -> set[Action]:
    actions = set[Action]([
        PlayTrainerAction(),
        SetupAction(),
        PlayBasicAction(),
        EvolveAction(),
        AbilityAction(),
        AttackAction(),
        RetreatAction(),
        PlaceEnergyAction(),
        SelectActiveAction(),
        SelectAction(),
        EndTurnAction(),
    ])
    return actions

def standard_effects() -> set[Effect]:
    return set[Effect]([
        DrawCardsEffect(),
        GetCardEffect(),
        SwitchMoveEffect(),
        EndTurnEffect(),
        SwapActiveEffect(),
        HealEffect(),
        DamageEffect(),
        DiscardEnergyEffect(),
    ])

def standard_damage_effects() -> set[DamageEffect]:
    return set[DamageEffect]([
        BaseDamageEffect(),
        EnergyBoostDamageEffect(),
    ])

def battle_factory(deck1:Deck, deck2:Deck, rules:Rules|None=None, actions:set[Action]|None=None, effects:set[Effect]|None=None, damage_effects:set[DamageEffect]|None=None):
    if actions is None:
        actions = standard_actions()
    if effects is None:
        effects = standard_effects()
    if damage_effects is None:
        damage_effects = standard_damage_effects()
    if rules is None:
        rules = Rules(actions, effects, damage_effects)
    state = BattleState(deck1, deck2, rules)
    return Battle(state)
    
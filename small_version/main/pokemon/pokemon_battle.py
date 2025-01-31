from pokemon.pokemon_card import PokemonCard
from pokemon.pokemon_types import EnergyType, Condition, EnergyContainer

import random
from dataclasses import dataclass, field
from collections import deque

class CantEvolveException(Exception):
    pass

class NoCardsToDrawException(Exception):
    pass

class ActivePokemon:

    def __init__(self, cards:list[PokemonCard], turns:int=0, damage:int=0, conditions:list[Condition]|None=None, energies:EnergyContainer|None=None):
        self.pokemon_cards = cards
        self.turns_in_active = turns
        self.damage = damage
        self.conditions = conditions if conditions is not None else list[Condition]()
        self.energies = energies if energies is not None else EnergyContainer()

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

    def end_turn(self) -> None:
        self.turns_in_active += 1

    def between_turns(self) -> None:
        pass

    def attach_energy(self, energy:EnergyType) -> None:
        self.energies = self.energies.add_energy(energy)

    def retreat(self, energies:EnergyContainer) -> None:
        self.energies = self.energies.remove_energies(energies)

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
    cards:tuple[PokemonCard]
    energies:tuple[EnergyType]
    
    def get_cards(self) -> tuple[PokemonCard]:
        """Get a list of the cards used in the deck

        :return: The cards in the deck
        :rtype: list[PokemonCard]
        """
        return self.cards

class DeckSetup:

    def __init__(self, deck:Deck, initial_hand_size:int, initial_energies:int, shuffle:bool=True,*, active:list[ActivePokemon]|None=None, discard:list[PokemonCard]|None=None, energy_discard:EnergyContainer|None=None):
        self.energies = list(deck.energies)
        cards = list(deck.cards)
        if shuffle:
            cards = self.__shuffle_deck_to_start(cards)
        self.deck = deque(cards[initial_hand_size:])
        self.hand = cards[0:initial_hand_size]
        self.active = active if active is not None else list[ActivePokemon]()
        self.discard = discard if discard is not None else list[PokemonCard]()
        self.energy_discard = energy_discard if discard is not None else EnergyContainer()
        self.next_energies = deque([self.__decide_next_energy() for _ in range(initial_energies)])

    def __shuffle_deck_to_start(self, cards:list[PokemonCard]) -> list[PokemonCard]:
        basics = [card for card in cards if card.is_basic()]
        starter = random.choice(basics)
        cards.remove(starter)
        random.shuffle(cards)
        cards.insert(0,starter)
        return cards

    def __decide_next_energy(self) -> EnergyType:
        return random.choice(self.energies)

    def bench(self) -> list[PokemonCard]:
        return self.active[1:]
    
    def bench_size(self) -> int:
        return len(self.active) - 1

    def start_turn(self, get_energy:bool=True, draw_card:bool=True) -> None:
        if get_energy:
            self.next_energies.append(self.__decide_next_energy())
        if draw_card:   
            card = self.deck.popleft()
            self.hand.append(card)

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

    def replace_starter(self, active_index:int) -> None:
        if active_index > 0:
            card = self.active.pop(active_index)
            self.active[0] = card

@dataclass
class OpponentDeckView:
    active:         list[ActivePokemon]
    hand_size:      int
    deck_size:      int
    energy_queue:   deque[EnergyType]
    discard_pile:   list[PokemonCard]
    energy_discard: EnergyContainer

@dataclass
class OwnDeckView:
    active:         list[ActivePokemon]
    hand:           list[PokemonCard]
    deck_size:      int
    energy_queue:   deque[EnergyType]
    discard_pile:   list[PokemonCard]
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
        active.append(a.copy())
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
        active.append(a.copy())
    return OwnDeckView(active, list(deck.hand), len(deck.deck), list(deck.next_energies), list(deck.discard), deck.energy_discard)

class Turn:

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.used_supporter = False
        self.retreated      = False
        self.energy_used    = False
        self.attacked       = False

@dataclass(frozen=True)
class Rules:
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
            if card.name() in card_names:
                card_names[card.name()] += 1
                if card_names[card.name()] > self.DUPLICATE_LIMIT:
                    return False
            else:
                card_names[card.name()] = 1
        return has_basic or not self.BASIC_REQUIRED

class BattleState:

    def __init__(self, deck1:Deck, deck2:Deck, rules:Rules|None, *, turn_number:int=0, next_move_team1:bool=True, team1_points:int=0, team2_points:int=0, team1_ready:bool=False, team2_ready:bool=False, current_turn:Turn|None=None):
        self.rules = rules if rules is not None else Rules()
        self.deck1 = DeckSetup(deck1, rules.INITIAL_HAND_SIZE, rules.FUTURE_ENERGIES, rules.SHUFFLE)
        self.deck2 = DeckSetup(deck2, rules.INITIAL_HAND_SIZE, rules.FUTURE_ENERGIES, rules.SHUFFLE)
        self.turn_number = turn_number
        self.next_move_team1 = next_move_team1
        self.team1_points = team1_points
        self.team2_points = team2_points
        self.team1_ready = team1_ready
        self.team2_ready = team2_ready
        self.current_turn = current_turn if current_turn is not None else Turn()

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
            self.next_move_team1 = not self.next_move_team1
            self.turn_number += 1
            self.current_turn.reset()
            self.between_turns()
            self.start_turn()
            return True
        return False
    
    def between_turns(self) -> None:
        self.deck1.between_turns()
        self.deck2.between_turns()

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
        if battle.team1_ready and is_team1 or battle.team2_ready and not is_team1:
            return False
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
        hand_index = inputs[0]
        deck = battle.current_deck()
        if self.is_valid(inputs):
            deck.play_basic(hand_index)
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if not battle.battle_going() or battle.need_to_replace_active():
            return False
        hand_index = inputs[0]
        deck = battle.current_deck()
        return battle.is_valid_basic_index(hand_index, deck) and deck.bench_size() < battle.rules.BENCH_SIZE

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

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if not battle.battle_going() or battle.need_to_replace_active():
            return False
        hand_index, active_index = inputs
        deck = battle.current_deck()
        valid1 = battle.is_valid_hand_index(hand_index, deck)
        valid2 = battle.is_valid_active_index(active_index, deck)
        if valid1 and valid2:
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

class AttackAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            attack_index = inputs[0]
            deck = battle.current_deck()
            defending_deck = battle.defending_deck()
            attack = deck.active[0].active_card().attacks[attack_index]

            attacked = defending_deck.active[0].active_card()
            defending_deck.take_damage(attack.base_damage, deck.active[0].active_card().get_energy_type())
            battle.current_turn.attacked = True
            if defending_deck.active[0] is None:
                if battle.team1_turn():
                    battle.team1_points += 1 if attacked.level <= 100 else 2
                else:
                    battle.team2_points += 1 if attacked.level <= 100 else 2
                self.next_move_team1 = not self.next_move_team1
            else:
                battle.end_turn()
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if not battle.need_to_replace_active() and battle.battle_going():
            deck = battle.current_deck()
            attack_index = inputs[0]
            if attack_index >= 0 and attack_index < len(deck.active[0].active_card().attacks):
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
        if len(deck.active) > 0:
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
            return True
        return False

    def is_valid(self, battle:BattleState, inputs:tuple[int, EnergyContainer]) -> bool:
        if not battle.battle_going() or battle.need_to_replace_active():
            return False
        active_index, energies = inputs
        deck = battle.current_deck()
        if battle.is_valid_active_index(active_index, deck):
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
                if token.upper() in EnergyType:
                    energies = energies.add_energy(EnergyType[token.upper()])
                else:
                    return False, None
            return True, (active_index, energies)
        return False, None

    def could_act(self, battle:BattleState) -> bool:
        if not battle.battle_going() or battle.need_to_replace_active():
            return False
        deck = battle.current_deck()
        return deck.active[0].active_card().retreat_cost <= deck.active[0].energies.size()

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
        if not battle.battle_going() and not battle.need_to_replace_active():
            return False
        active_index = inputs[0]
        deck = battle.current_deck()
        return battle.is_valid_active_index(active_index, deck) and not battle.current_turn.energy_used

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

class SelectAction(Action):
    def action(self, battle:BattleState, inputs:tuple[int]) -> bool:
        if self.is_valid(battle, inputs):
            bench_index = inputs[0]
            deck = battle.current_deck()
            deck.replace_starter(bench_index)
            if battle.need_to_replace_active():
                self.next_move_team1 = not self.next_move_team1
            else:
                self.next_move_team1 = battle.team1_turn()
                if battle.current_turn.attacked:
                    battle.end_turn()
            return True
        return False  

    def is_valid(self, battle:BattleState, inputs:tuple[int]) -> bool:
        bench_index = inputs[0]
        deck = battle.current_deck()
        return battle.need_to_replace_active() and battle.is_valid_bench_index(bench_index, deck)

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
        return "select"

    def action_description(self) -> str:
        return "Select a new active pokemon"
    
    def input_format(self) -> str:
        return "select x"

class EndTurnAction(Action):
    def action(self, battle:BattleState, inputs:tuple) -> bool:
        battle.end_turn()

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        return battle.battle_going()

    def is_valid_raw(self, inputs:tuple[str]) -> tuple[bool, tuple]:
        return len(inputs) == 0

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

    def __init__(self, actions:dict[str,Action], state:BattleState):
        self.actions = actions
        self.state = state

    def team1_move(self) -> bool:
        return self.state.team1_move()
    
    def team1_turn(self) -> bool:
        return self.state.team1_turn()

    def is_over(self) -> bool:
        return self.state.is_over()
    
    def action(self, action:str, inputs:tuple) -> bool:
        if action in self.actions:
            success = self.actions[action].action(self.state, inputs)
            return success
        return False
    
    def available_actions(self) -> list[str]:
        return {name:action for name,action in self.actions.items() if action.could_act(self.state)}

    def get_rules(self) -> Rules:
        return self.state.rules
    
    def get_score(self) -> tuple[int]:
        return self.state.team1_points, self.state.team2_points

def standard_actions() -> dict[str, Action]:
    actions = list[Action]([
        SetupAction(),
        PlayBasicAction(),
        EvolveAction(),
        AttackAction(),
        RetreatAction(),
        PlaceEnergyAction(),
        SelectAction(),
        EndTurnAction()
    ])
    return {action.action_name():action for action in actions}

def battle_factory(deck1:Deck, deck2:Deck, rules:Rules|None=None, actions:dict[str,Action]|None=None):
    if rules is None:
        rules = Rules()
    if actions is None:
        actions = standard_actions()
    state = BattleState(deck1, deck2, rules)
    return Battle(actions, state)
    
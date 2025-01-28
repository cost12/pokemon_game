from pokemon.pokemon_card import PokemonCard
from pokemon.pokemon_types import EnergyType, Condition, EnergyContainer

import random
from dataclasses import dataclass, field

class CantEvolveException(Exception):
    pass

class NoCardsToDrawException(Exception):
    pass

@dataclass(frozen=True)
class ActivePokemon:
    pokemon_cards:tuple[PokemonCard]
    turns_in_active:int = 0
    damage:int=0
    condition:Condition=field(default=Condition.NONE)
    energies:EnergyContainer=field(default=EnergyContainer())

    def active_card(self) -> PokemonCard:
        """The card that is currently on top/ highest evolved

        :return: The card that is currently on top/ highest evolved
        :rtype: PokemonCard
        """
        return self.pokemon_cards[0]

    def evolve(self, card:PokemonCard) -> 'ActivePokemon':
        """Evolves the active pokemon

        :param card: The card to evolve to
        :type card: PokemonCard
        :return: The evolved card
        :rtype: ActivePokemon
        """
        return ActivePokemon((card, *self.pokemon_cards), 0, self.damage, Condition.NONE, self.energies)

    def hp(self) -> int:
        """The remaining health of the pokemon

        :return: The remaining health of the pokemon
        :rtype: int
        """
        return max(self.active_card().hit_points - self.damage, 0)

    def end_turn(self) -> 'ActivePokemon':
        """Completes the actions that happen when a turn ends

        :return: The ActivePokemon after the turn ends
        :rtype: ActivePokemon
        """
        return ActivePokemon(self.pokemon_cards, self.turns_in_active+1, self.damage, self.condition, self.energies)

    def between_turns(self) -> 'ActivePokemon':
        return self

    def attach_energy(self, energy:EnergyType) -> 'ActivePokemon':
        """Adds an energy to the card

        :param energy: The type of energy to attach
        :type energy: EnergyType
        :return: The ActivePokemon after the energy is attached
        :rtype: ActivePokemon
        """
        return ActivePokemon(self.pokemon_cards, self.turns_in_active, self.damage, self.condition, self.energies.add_energy(energy))

    def retreat(self, energies:EnergyContainer) -> 'ActivePokemon':
        """Discards the required energies and returns true if it can retreat, otherwise returns false

        :param energies: The energies to discard
        :type energies: dict[EnergyType,int]
        :return: The resulting ActivePokemon
        :rtype: ActivePokemon
        """
        return ActivePokemon(self.pokemon_cards, self.turns_in_active, self.damage, self.condition, self.energies.remove_energies(energies))

    def take_damage(self, amount:int, damage_type:EnergyType) -> 'ActivePokemon':
        total = amount
        if damage_type == self.active_card().get_resistance():
            total -= 20
        if damage_type == self.active_card().get_weakness():
            total += 20
        return ActivePokemon(self.pokemon_cards, self.turns_in_active, self.damage + total, self.condition, self.energies)
    
    def is_knocked_out(self):
        return self.hp() <= 0

    def get_energies(self) -> EnergyContainer:
        return self.energies

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

@dataclass(frozen=True)
class DeckSetup:
    energies       :tuple[EnergyType]
    deck           :tuple[PokemonCard]
    hand           :tuple[PokemonCard]
    active         :tuple[ActivePokemon]
    discard        :tuple[PokemonCard]
    energy_discard :EnergyContainer
    next_energies  :tuple[EnergyType]

    def next_energy(self) -> EnergyType:
        return random.choice(self.energies)

    def bench(self) -> list[PokemonCard]:
        return self.active[1:]
    
    def bench_size(self) -> int:
        return len(self.active) - 1

    def start_turn(self, get_energy:bool=True, draw_card:bool=True) -> 'DeckSetup':
        next = list(self.next_energies)
        hand = list(self.hand)
        deck = list(self.deck)
        if get_energy:
            next.append(self.next_energy())
        if draw_card:   
            card = deck.pop(0)
            hand.append(card)
        return DeckSetup(self.energies, tuple(deck), tuple(hand), self.active, self.discard, self.energy_discard, tuple(next))

    def between_turns(self) -> 'DeckSetup':
        active = list(self.active)
        for i in range(len(active)):
            active[i] = active[i].between_turns()
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, self.next_energies)

    def end_turn(self) -> 'DeckSetup':
        active = list(self.active)
        for i in range(len(active)):
            active[i] = active[i].end_turn()
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, self.next_energies)

    def play_card_from_hand(self, hand_index:int) -> 'DeckSetup':
        discard = list(self.discard)
        hand = list(self.hand)
        card = hand.pop(hand_index)
        discard.append(card)
        return DeckSetup(self.energies, self.deck, tuple(hand), self.active, tuple(discard), self.energy_discard, self.next_energies)

    def evolve(self, hand_index:int, active_index:int) -> 'DeckSetup':
        active = list(self.active)
        hand = list(self.hand)
        card = hand.pop(hand_index)
        active[active_index] = active[active_index].evolve(card)
        return DeckSetup(self.energies, self.deck, tuple(hand), tuple(active), self.discard, self.energy_discard, self.next_energies)

    def retreat(self, active_index:int, energies:EnergyContainer) -> 'DeckSetup':
        if active_index == 0: return self
        active = list(self.active)
        to_bench = active[0].retreat(energies)
        energy_discard = self.energy_discard.add_energies(energies)
        active[0] = active[active_index]
        active[active_index] = to_bench
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, tuple(energy_discard), self.next_energies)

    def take_damage(self, amount:int, damage_type:EnergyType) -> 'DeckSetup':
        active = list(self.active)
        active[0] = active[0].take_damage(amount, damage_type)
        if active[0].is_knocked_out():
            return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, self.next_energies).discard_from_active(0)
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, self.next_energies)

    def shuffle_hand_into_deck(self) -> 'DeckSetup':
        deck = list(self.deck)
        deck.extend(self.hand)
        random.shuffle(deck)
        return DeckSetup(self.energies, tuple(deck), tuple(), self.active, self.discard, self.energy_discard, self.next_energies)

    def discard_from_active(self, active_index:int) -> 'DeckSetup':
        discard = list(discard)
        active = list(self.active)
        discard.extend(active[active_index].get_cards())
        energies = active[active_index].get_energies()
        energy_discard = self.energy_discard.add_energies(energies)
        if active_index == 0:
            active[active_index] = None
        else:
            active.pop(active_index)
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), tuple(discard), tuple(energy_discard), self.next_energies)

    def attach_energy(self, active_index:int) -> 'DeckSetup':
        next_energies = list(self.next_energies)
        active = list(self.active)
        energy_type = next_energies.pop(0)
        active[active_index] = active[active_index].attach_energy(energy_type)
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, tuple(next_energies))

    def delete_energy(self) -> 'DeckSetup':
        next_energies = list(self.next_energies)
        next_energies.pop(0)
        return DeckSetup(self.energies, self.deck, self.hand, self.active, self.discard, self.energy_discard, tuple(next_energies))

    def play_basic(self, hand_index:int) -> 'DeckSetup':
        active = list(self.active)
        hand = list(self.hand)
        active.append(ActivePokemon((self.hand[hand_index],)))
        hand.pop(hand_index)
        return DeckSetup(self.energies, self.deck, tuple(hand), tuple(active), self.discard, self.energy_discard, self.next_energies)

    def replace_starter(self, active_index:int) -> 'DeckSetup':
        if active_index > 0:
            active = list(self.active)
            active[0] = active[active_index]
            active.pop(active_index)
            return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, self.next_energies)
        return DeckSetup(self.energies, self.deck, self.hand, tuple(active), self.discard, self.energy_discard, self.next_energies)

@dataclass(frozen=True)
class OpponentDeckView:
    active: tuple[ActivePokemon]
    hand_size: int
    deck_size: int
    energy_queue: tuple[EnergyType]
    discard_pile: tuple[PokemonCard]
    energy_discard: EnergyContainer
    bench_size: int

@dataclass(frozen=True)
class OwnDeckView:
    active: tuple[ActivePokemon]
    hand: tuple[PokemonCard]
    deck_size: int
    energy_queue: tuple[EnergyType]
    discard_pile: tuple[PokemonCard]
    energy_discard: EnergyContainer
    bench_size: int

def get_opponent_deck_view(deck:DeckSetup) -> OpponentDeckView:
    """Get a view of a DeckSetup without the ability to change the DeckSetup

    :param deck: The deck to view
    :type deck: DeckSetup
    :return: The immutable partial view of the deck
    :rtype: DeckView
    """
    return OpponentDeckView(tuple(deck.active), len(deck.hand), len(deck.deck), tuple(deck.next_energies), tuple(deck.discard), deck.energy_discard, deck.BENCH_SIZE)

def get_own_deck_view(deck:DeckSetup) -> OpponentDeckView:
    """Get a view of a DeckSetup without the ability to change the DeckSetup

    :param deck: The deck to view
    :type deck: DeckSetup
    :return: The immutable partial view of the deck
    :rtype: DeckView
    """
    return OwnDeckView(tuple(deck.active), tuple(deck.hand), len(deck.deck), tuple(deck.next_energies), tuple(deck.discard), deck.energy_discard, deck.BENCH_SIZE)

@dataclass(frozen=True)
class Turn:
    used_supporter :bool = False
    retreated      :bool = False
    energy_used    :bool = False
    attacked       :bool = False

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

@dataclass(frozen=True)
class BattleState:
    deck1           :DeckSetup
    deck2           :DeckSetup
    rules           :Rules
    turn_number     :int = 0
    next_move_team1 :bool = True
    team1_points    :int = 0
    team2_points    :int = 0
    team1_ready     :bool = False
    team2_ready     :bool = False
    current_turn    :Turn = field(default=Turn)

    def team1_move(self) -> bool:
        return self.next_move_team1
    
    def team1_turn(self) -> bool:
        return self.turn_number % 2 == 0
    
    def current_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck1
        return self.deck2
    
    def update_current_deck(self, deck:DeckSetup) -> 'BattleState':
        if self.team1_move():
            return BattleState(deck, self.deck2, self.rules, self.turn_number, self.next_move_team1, self.team1_points, self.team2_points, self.team1_ready, self.team2_ready, self.current_turn)
        return BattleState(self.deck1, deck, self.rules, self.turn_number, self.next_move_team1, self.team1_points, self.team2_points, self.team1_ready, self.team2_ready, self.current_turn)

    def is_over(self) -> bool:
        return self.team1_points >= self.rules.POINTS_TO or self.team2_points >= self.rules.POINTS_TO or \
                (self.deck1.active[0] is None and self.deck1.bench_size() == 0) or \
                (self.deck2.active[0] is None and self.deck2.bench_size() == 0)
    
    def battle_going(self) -> bool:
        return self.team1_ready and self.team2_ready and not self.is_over()

class Action:
    """Represents an action a player can make in a battle
    Has no state, but manipulates battle state
    Will likely need to break Battle into Battle and BattleState where Battle contains BattleState and also Actions that are valid for the battle
    Also, maybe a Rules class or something to hold things like DECK_SIZE, DUPLICATE_LIMIT, etc
    """

    def action(self, battle:BattleState, inputs:tuple) -> tuple[bool, BattleState]:
        pass

    def is_valid(self, battle:BattleState, inputs:tuple) -> bool:
        pass

    def is_valid_raw(self, inputs:tuple) -> tuple[bool, tuple]:
        pass

    def could_act(self, battle:BattleState) -> bool:
        pass

    def action_name(self) -> str:
        pass

    def action_description(self) -> str:
        pass

class SetupAction(Action):
    def action(self, battle:BattleState, inputs:tuple[bool, int]) -> tuple[bool, BattleState]:
        if not self.is_valid(battle, inputs):
            return False, battle
        for i in range(1,len(inputs)):
            subtract = 0
            for j in range(i):
                if inputs[j] < inputs[i]:
                    subtract += 1
            battle = battle.update_current_deck(battle.current_deck().play_basic(inputs[i]-subtract))
        if inputs[0]:
            battle = BattleState(battle.deck1, battle.deck2, battle.rules, battle.turn_number, battle.next_move_team1, battle.team1_points, battle.team2_points, True, battle.team2_ready, battle.current_turn)
        else:
            battle = BattleState(battle.deck1, battle.deck2, battle.rules, battle.turn_number, battle.next_move_team1, battle.team1_points, battle.team2_points, battle.team1_ready, True, battle.current_turn)
        return True, battle
    
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
            if index < 0 or index >= len(battle.current_deck().hand) or not battle.current_deck().hand[index].is_basic():
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

class Battle:
    """Represents a battle between two decks of cards
    """

    def __init__(self, actions:dict[str,Action], state:BattleState):
        self.state = state
        self.actions = actions

    def team1_move(self) -> bool:
        return self.state.team1_move()
    
    def team1_turn(self) -> bool:
        return self.state.team1_turn()

    def is_over(self) -> bool:
        return self.state.is_over()
    
    def action(self, action:str, inputs:tuple) -> bool:
        if action in self.actions:
            success, self.state = self.actions[action].action(inputs)
            return success
        return False
    
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
    
    def __verify_bench_index(self, index:int, deck:DeckSetup) -> bool:
        return index > 0 and index < len(deck.active)

    def __current_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck1
        return self.deck2

    def __defending_deck(self) -> DeckSetup:
        if self.team1_move():
            return self.deck2
        return self.deck1
    
    def need_to_replace_active(self) -> bool:
        return len(self.deck1.active) == 0 or self.deck1.active[0] is None or \
               len(self.deck2.active) == 0 or self.deck2.active[0] is None

    def play_card(self, hand_index:int) -> bool:
        return False
    
    def can_play_basic(self, hand_index:int) -> bool:
        if not self.__battle_going() or self.need_to_replace_active():
            return False
        deck = self.__current_deck()
        return self.__verify_basic_index(hand_index, deck) and deck.bench_size() < deck.BENCH_SIZE

    def could_play_basic(self) -> bool:
        deck = self.__current_deck()
        for hand_index in range(len(deck.hand)):
            if self.can_play_basic(hand_index):
                return True
        return False

    def play_basic(self, hand_index:int) -> bool:
        deck = self.__current_deck()
        if self.can_play_basic(hand_index):
            deck.play_basic(hand_index)
            return True
        return False
    
    def can_evolve(self, hand_index:int, active_index:int) -> bool:
        if not self.__battle_going() or self.need_to_replace_active():
            return False
        deck = self.__current_deck()
        valid1 = self.__verify_hand_index(hand_index, deck)
        valid2 = self.__verify_active_index(active_index, deck)
        if valid1 and valid2:
            if deck.active[active_index].turns_in_active >= self.TURNS_TO_EVOLVE and \
               deck.hand[hand_index].evolves_from() == deck.active[active_index].active_card().pokemon:
                return True
        return False

    def could_evolve(self) -> bool:
        deck = self.__current_deck()
        for hand_index in range(len(deck.hand)):
            for active_index in range(len(deck.active)):
                if self.can_evolve(hand_index, active_index):
                    return True
        return False

    def evolve(self, hand_index:int, active_index:int) -> bool:
        if self.can_evolve(hand_index, active_index):
            deck = self.__current_deck()
            deck.evolve(hand_index, active_index)
            return True
        return False

    def can_retreat(self, active_index:int, energies:EnergyContainer) -> bool:
        if not self.__battle_going() or self.need_to_replace_active():
            return False
        deck = self.__current_deck()
        valid = self.__verify_active_index(active_index, deck)
        if valid:
            if deck.bench_size() > 0 and deck.active[0].active_card().retreat_cost == energies.size() and deck.active[0].energies.at_least_as_big(energies):
                return True
        return False

    def could_retreat(self) -> bool:
        if not self.__battle_going() or self.need_to_replace_active():
            return False
        deck = self.__current_deck()
        return deck.active[0].active_card().retreat_cost <= deck.active[0].energies.size()

    def retreat(self, active_index:int, energies:EnergyContainer) -> bool:
        if self.can_retreat(active_index, energies):
            deck = self.__current_deck()
            deck.retreat(active_index, energies)
            return True
        return False

    def can_attack(self, attack_index:int) -> bool:
        if not self.need_to_replace_active() and self.__battle_going():
            deck = self.__current_deck()
            if attack_index >= 0 and attack_index < len(deck.active[0].active_card().attacks):
                return deck.active[0].energies.at_least_as_big(deck.active[0].active_card().attacks[attack_index].energy_cost)
        return False

    def could_attack(self) -> bool:
        deck = self.__current_deck()
        for attack_index in range(len(deck.active[0].active_card().attacks)):
            if self.can_attack(attack_index):
                return True
        return False

    def attack(self, attack_index:int) -> bool:
        deck = self.__current_deck()
        if self.can_attack(attack_index):
            attack = deck.active[0].active_card().attacks[attack_index]

            attacked = self.__defending_deck().active[0].active_card()
            self.__defending_deck().take_damage(attack.base_damage, deck.active[0].active_card().get_energy_type())
            self.turn.attacked = True
            if self.__defending_deck().active[0] is None:
                if self.team1_turn():
                    self.team1_points += 1 if attacked.level <= 100 else 2
                else:
                    self.team2_points += 1 if attacked.level <= 100 else 2
                self.next_move_team1 = not self.next_move_team1
            else:
                self.end_turn()
            return True
        return False

    def use_ability(self, ability_index:int) -> bool:
        return False

    def can_select(self, index:int) -> bool:
        deck = self.__current_deck()
        return self.need_to_replace_active() and self.__verify_bench_index(index, deck)

    def could_select(self) -> bool:
        deck = self.__current_deck()
        for i in range(1, len(deck.active)):
            if self.can_select(i):
                return True
        return False

    def select(self, index:int) -> bool:
        if self.can_select(index):
            deck = self.__current_deck()
            deck.replace_starter(index)
            if self.need_to_replace_active():
                self.next_move_team1 = not self.next_move_team1
            else:
                self.next_move_team1 = self.team1_turn()
                if self.turn.attacked:
                    self.end_turn()
            return True
        return False

    def can_place_energy(self, active_index:int) -> bool:
        if not self.__battle_going() and not self.need_to_replace_active():
            return False
        deck = self.__current_deck()
        valid = self.__verify_active_index(active_index, deck)
        return valid and not self.turn.energy_used

    def could_place_energy(self) -> bool:
        deck = self.__current_deck()
        for i in range(len(deck.active)):
            if self.can_place_energy(i):
                return True
        return False

    def place_energy(self, active_index:int) -> bool:
        deck = self.__current_deck()
        if self.can_place_energy(active_index):
            deck.attach_energy(active_index)
            self.turn.energy_used = True
            return True
        return False

    def between_turns(self) -> None:
        self.deck1.between_turns()
        self.deck2.between_turns()

    def start_turn(self, generate_energy:bool=True) -> None:
        deck = self.__current_deck()
        draw_card = len(deck.deck) > 0 and len(deck.hand) < self.MAX_HAND_SIZE
        deck.start_turn(generate_energy, draw_card)
        self.turn.energy_used = not generate_energy

    def could_end_turn(self) -> bool:
        return self.__battle_going()

    def end_turn(self) -> bool:
        if self.could_end_turn():
            if not self.turn.energy_used:
                self.__current_deck().delete_energy()
            self.__current_deck().end_turn()
            self.next_move_team1 = not self.next_move_team1
            self.turn_number += 1
            self.turn.reset()
            self.between_turns()
            self.start_turn()
            return True
        return False
    
    def available_actions(self) -> list[str]:
        if not self.__battle_going():
            if not self.is_over():
                return ['play']
            return []
        if self.could_select():
            return ['select', 'new_active']
        moves = []
        if self.could_play_basic():
            moves.append('play_basic')
        if self.could_retreat():
            moves.append('retreat')
        if self.could_evolve():
            moves.append('evolve')
        if self.could_attack():
            moves.append('attack')
        if self.could_place_energy():
            moves.append('place_energy')
        if self.could_end_turn():
            moves.append('end_turn')
        return moves
    
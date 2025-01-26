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

class DeckSetup:

    def __init__(self, cards:list[PokemonCard], energies:list[EnergyType], *, 
                 initial_hand_size:int=5, future_energies:int=1):
        """Represents the way a deck is set during a battle

        :param cards: The pokemon cards in the deck
        :type cards: list[PokemonCard]
        :param energies: The available energy types to be used
        :type energies: list[EnergyType]
        """
        self.energies = list[EnergyType](energies)

        self.hand           = cards[0:initial_hand_size]
        self.active         = list[ActivePokemon]()
        self.discard        = list[PokemonCard]()
        self.energy_discard = EnergyContainer()
        self.deck           = cards[initial_hand_size:]
        self.next_energies  = list[EnergyType]()
        for _ in range(future_energies):
            self.__get_energy()

    def __get_energy(self) -> None:
        """Generates the next energy
        """
        self.next_energies.append(random.choice(self.energies))

    def bench(self) -> list[PokemonCard]:
        return self.active[1:]
    
    def bench_size(self) -> int:
        return len(self.active) - 1

    def start_turn(self, get_energy:bool=True, draw_card:bool=True) -> None:
        """Updates the deck for a new turn

        :param get_energy: True if the player gets an energy this turn. This is only false for the first player's first turn, defaults to True
        :type get_energy: bool, optional
        :raises NoCardsToDrawException: When there are no cards left in the deck
        """
        if get_energy:
            self.__get_energy()
        if draw_card:   
            self.draw_card()

    def between_turns(self) -> None:
        for i in range(len(self.active)):
            self.active[i] = self.active[i].between_turns()

    def end_turn(self) -> None:
        for i in range(len(self.active)):
            self.active[i] = self.active[i].end_turn()

    def draw_card(self) -> None:
        """Updates the deck for a drawn card
        """
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

    def retreat(self, active_index:int, energies:EnergyContainer) -> bool:
        """Updates the card to represent the active pokemon retreating

        :param active_index: The index of the new card to put out
        :type active_index: int
        :param energies: The energies to discard if the retreat is successful
        :type energies: EnergyContainer
        :return: True if the retreat was successful
        :rtype: bool
        """
        if active_index == 0: return False
        temp = self.active[0].retreat(energies)
        self.energy_discard = self.energy_discard.add_energies(energies)
        self.active[0] = self.active[active_index]
        self.active[active_index] = temp
        return True

    def take_damage(self, amount:int, damage_type:EnergyType) -> None:
        self.active[0] = self.active[0].take_damage(amount, damage_type)
        if self.active[0].is_knocked_out():
            self.discard_from_active(0)

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
        self.energy_discard = self.energy_discard.add_energies(energies)
        if active_index == 0:
            self.active[active_index] = None
        else:
            self.active.pop(active_index)

    def attach_energy(self, active_index:int) -> None:
        energy_type = self.next_energies.pop(0)
        self.active[active_index] = self.active[active_index].attach_energy(energy_type)

    def delete_energy(self) -> None:
        self.next_energies.pop(0)

    def play_basic(self, hand_index:int) -> None:
        """Plays a basic card from the hand to a new spot on the bench

        :param hand_index: The index of the card in the hand
        :type hand_index: int
        """
        self.active.append(ActivePokemon((self.hand[hand_index],)))
        self.hand.pop(hand_index)

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

class Turn:

    def __init__(self):
        self.reset()

    def reset(self):
        self.used_supporter = False
        self.retreated = False
        self.energy_used = False
        self.attacked = False

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

    def is_over(self) -> bool:
        return self.team1_points >= self.rules.POINTS_TO or self.team2_points >= self.rules.POINTS_TO or \
                (self.deck1.active[0] is None and self.deck1.bench_size() == 0) or \
                (self.deck2.active[0] is None and self.deck2.bench_size() == 0)

class Action:
    """Represents an action a player can make in a battle
    Has no state, but manipulates battle state
    Will likely need to break Battle into Battle and BattleState where Battle contains BattleState and also Actions that are valid for the battle
    Also, maybe a Rules class or something to hold things like DECK_SIZE, DUPLICATE_LIMIT, etc
    """

    def action(self, battle:'Battle', inputs:tuple) -> None:
        pass

    def is_valid(self, battle:'Battle', inputs:tuple) -> None:
        pass

    def could_act(self, battle:'Battle', inputs:tuple) -> None:
        pass

    def action_name(self) -> str:
        pass

    def action_description(self) -> str:
        pass

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
            deck.play_basic(to_play[i]-subtract)
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
    
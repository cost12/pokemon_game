from pokemon.pokemon_battle import ActivePokemon, DeckSetup, Deck, Battle
from pokemon.pokemon_types import Condition, EnergyContainer, EnergyType
from pokemon.pokemon_card import PokemonCard
from pokemon.pokemon_collections import generate_attacks, generate_pokemon, generate_pokemon_cards

from frozendict import frozendict
import pytest

# TESTING FOR ActivePokemon
def get_cards() -> dict[str, PokemonCard]:
    attacks = generate_attacks()
    pokemon = generate_pokemon()
    return generate_pokemon_cards(pokemon, attacks)

def get_bulbasaur(cards:dict[str, PokemonCard]):
    return ActivePokemon((cards['Bulbasaur'],))

def get_ivysaur(cards:dict[str, PokemonCard]):
    return ActivePokemon((cards['Ivysaur'], cards['Bulbasaur']))

def set_turns_in_active(active:ActivePokemon, turns:int) -> ActivePokemon:
    return ActivePokemon(active.pokemon_cards, turns, active.damage, active.condition, active.energies)

def set_damage(active:ActivePokemon, damage:int) -> ActivePokemon:
    return ActivePokemon(active.pokemon_cards, active.turns_in_active, damage, active.condition, active.energies)

def test_default():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    assert active.turns_in_active == 0
    assert active.damage == 0
    assert active.condition == Condition.NONE
    assert isinstance(active.energies, EnergyContainer)

def test_evolve():
    cards  = get_cards()
    active = get_bulbasaur(cards)

    active = set_turns_in_active(active, 1)
    new_active = active.evolve(cards['Ivysaur'])
    assert new_active.active_card() == cards['Ivysaur']
    assert new_active.turns_in_active == 0

    new_active = new_active.evolve(cards['Venusaur ex'])
    assert new_active.active_card() == cards['Venusaur ex']

def test_hp():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    assert active.hp() == 70
    active = set_damage(active, 50)
    assert active.hp() == 20
    active = set_damage(active, 70)
    assert active.hp() == 0
    active = set_damage(active, 100)
    assert active.hp() == 0

def test_end_turn():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    active = set_turns_in_active(active, 0)
    new_active = active.end_turn()
    assert new_active.turns_in_active == 1
    assert active.turns_in_active == 0

def test_between_turns():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    new_active = active.between_turns()
    assert active == new_active

def test_attach_energy():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    new_active = active.attach_energy(EnergyType.GRASS)
    assert active.energies.size() == 0
    assert new_active.energies.size() == 1
    new_active2 = new_active.attach_energy(EnergyType.GRASS)
    assert new_active.energies.size() == 1
    assert new_active2.energies.size() == 2

def test_retreat():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    
    active = active.attach_energy(EnergyType.GRASS)
    new_active = active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert active.energies.size() == 1
    assert new_active.energies.size() == 0

    with pytest.raises(Exception):
        new_active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))

    active = active.attach_energy(EnergyType.FIRE)
    new_active = active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert active.energies.size() == 2
    assert new_active.energies.size() == 1
    assert new_active.energies.size_of(EnergyType.FIRE) == 1

    with pytest.raises(Exception):
        active.retreat(EnergyContainer(frozendict({EnergyType.METAL:1})))

def test_take_damage():
    cards  = get_cards()
    active = get_bulbasaur(cards)

    new_active = active.take_damage(10, EnergyType.FIRE)
    assert new_active.hp() == 40
    assert active.hp() == 70

    new_active = active.take_damage(10, EnergyType.GRASS)
    assert new_active.hp() == 60
    assert active.hp() == 70

    new_active = active.take_damage(100, EnergyType.GRASS)
    assert new_active.hp() == 0
    assert active.hp() == 70

def test_knocked_out():
    cards  = get_cards()
    active = get_bulbasaur(cards)

    new_active = active.take_damage(100, EnergyType.GRASS)
    assert new_active.is_knocked_out()

    new_active = active.take_damage(70, EnergyType.GRASS)
    assert new_active.is_knocked_out()
# END OF TESTING FOR ActivePokemon


# TESTING FOR DeckSetup
def get_deck():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur'],
        cards['Ivysaur'],
        cards['Venusaur'],
        cards['Bulbasaur'],
        cards['Ivysaur'],
        cards['Venusaur'],
        cards['Charmander'],
        cards['Charmeleon'],
        cards['Charizard'],
        cards['Charmander'],
        cards['Charmeleon'],
        cards['Charizard']
    ]
    return Deck("name", deck_cards, (EnergyType.GRASS,EnergyType.FIRE))

def place_basic(deck:DeckSetup) -> bool:
    for card in deck.hand:
        if card.is_basic():
            deck.hand.remove(card)
            deck.active.append(ActivePokemon((card,)))
            return True
    for card in deck.deck:
        if card.is_basic():
            deck.deck.remove(card)
            deck.active.append(ActivePokemon((card,)))
            return True
    return False

def place_evolution_in_hand(deck:DeckSetup, active_index:int, hand_index:int) -> bool:
    for card in deck.hand:
        if card.evolves_from() == deck.active[active_index].active_card().pokemon:
            deck.hand.remove(card)
            deck.hand.insert(hand_index, card)
            return True
    for card in deck.deck:
        if card.evolves_from() == deck.active[active_index].active_card().pokemon:
            deck.deck.remove(card)
            deck.hand.insert(hand_index, card)
            return True
    return False

def evolve(deck:DeckSetup, active_index:int) -> bool:
    for card in deck.hand:
        if card.evolves_from(deck.active[active_index]):
            deck.hand.remove(card)
            cards = deck.active[active_index].get_cards()
            cards.insert(0, card)
            damage = deck.active[active_index].damage
            energies = deck.active[active_index].energies
            deck.active[active_index] = ActivePokemon(tuple(cards),damage=damage, energies=energies)
            return True
    for card in deck.deck:
        if card.evolves_from(deck.active[active_index]):
            deck.deck.remove(card)
            cards = deck.active[active_index].get_cards()
            cards.insert(0, card)
            damage = deck.active[active_index].damage
            energies = deck.active[active_index].energies
            deck.active[active_index] = ActivePokemon(tuple(cards),damage=damage, energies=energies)
            return True
    return False

def set_turns_in_active_deck(deck:DeckSetup, active_index:int, turns:int):
    cards = deck.active[active_index].pokemon_cards
    damage = deck.active[active_index].damage
    condition = deck.active[active_index].condition
    energies = deck.active[active_index].energies
    deck.active[active_index] = ActivePokemon(cards, turns, damage, condition, energies)

def place_energy(deck:DeckSetup, active_index:int, energy:EnergyType):
    cards = deck.active[active_index].pokemon_cards
    turns = deck.active[active_index].turns_in_active
    damage = deck.active[active_index].damage
    condition = deck.active[active_index].condition
    energies = deck.active[active_index].energies.add_energy(energy)
    deck.active[active_index] = ActivePokemon(cards, turns, damage, condition, energies)

def same_cards(cards:list[PokemonCard], deck:DeckSetup):
    deck_cards = []
    deck_cards.extend(deck.deck)
    deck_cards.extend(deck.hand)
    deck_cards.extend(deck.discard)
    for active in deck.active:
        deck_cards.extend(active.get_cards())
    for i in range(len(cards)):
        if cards[i] in deck_cards:
            deck_cards.remove(cards[i])
        else:
            return False
    return len(deck_cards) == 0

def test_setup():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    size = len(deck.cards)

    assert len(deck_setup.next_energies) == deck_setup.FUTURE_ENERGIES
    assert len(deck_setup.hand) == deck_setup.INITIAL_HAND_SIZE
    assert len(deck_setup.hand) + len(deck_setup.deck) == size

def test_start_turn():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    # no energy
    deck_setup.start_turn(False)
    assert len(deck_setup.next_energies) == deck_setup.FUTURE_ENERGIES
    assert len(deck_setup.hand) - 1 == deck_setup.INITIAL_HAND_SIZE
    # yes energy
    deck_setup = DeckSetup(deck.cards, deck.energies)
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == deck_setup.FUTURE_ENERGIES
    assert len(deck_setup.hand) - 1 == deck_setup.INITIAL_HAND_SIZE
    # hand full
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=5, max_hand_size=5)
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == deck_setup.FUTURE_ENERGIES
    assert len(deck_setup.hand) == deck_setup.INITIAL_HAND_SIZE
    # deck empty
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=len(deck.cards), max_hand_size=len(deck.cards))
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == deck_setup.FUTURE_ENERGIES
    assert len(deck_setup.hand) == deck_setup.INITIAL_HAND_SIZE

def test_between_turns():
    pass

def test_end_turn():
    pass

def test_draw_card():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    # normal
    deck_setup = DeckSetup(deck.cards, deck.energies)
    assert deck_setup.draw_card()
    assert len(deck_setup.hand) - 1 == deck_setup.INITIAL_HAND_SIZE
    # hand full
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=5, max_hand_size=5)
    assert not deck_setup.draw_card()
    assert len(deck_setup.hand) == deck_setup.INITIAL_HAND_SIZE
    # deck empty
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=len(deck.cards), max_hand_size=len(deck.cards))
    assert not deck_setup.start_turn()
    assert len(deck_setup.hand) == deck_setup.INITIAL_HAND_SIZE

def test_play_card_from_hand():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    deck_setup.play_card_from_hand(0)
    assert same_cards(deck.cards, deck_setup)
    assert len(deck_setup.hand) == deck_setup.INITIAL_HAND_SIZE - 1
    assert len(deck_setup.discard) == 1

def test_evolve():
    # TO TEST: figure out where error checking for evolving should go
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)

    place_basic(deck_setup)
    place_evolution_in_hand(deck_setup, 0, 0)
    pass

# END OF TESTING FOR DeckSetup

# FULL BATTLE TESTING
def deterministic_battle_setup(deck_cards:list[PokemonCard]) -> Battle:
    deck = Deck("name1", deck_cards, (EnergyType.GRASS,))
    battle = Battle(deck, deck, deck_size=12, duplicate_limit=3)
    battle.deck1 = DeckSetup(deck.cards, deck.energies)
    battle.deck2 = DeckSetup(deck.cards, deck.energies)
    return battle

def test_battle():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur'],
        cards['Ivysaur'],
        cards['Venusaur'],
        cards['Venusaur ex'],
        cards['Bulbasaur'],
        cards['Ivysaur'],
        cards['Venusaur'],
        cards['Venusaur ex'],
        cards['Bulbasaur'],
        cards['Ivysaur'],
        cards['Venusaur'],
        cards['Venusaur ex']
    ]
    battle = deterministic_battle_setup(deck_cards)
    # setup: both teams place Bulbasuar to active
    assert battle.team1_setup((0,))
    assert battle.team2_setup((0,))
    # Team 1 turn 1: card is drawn
    assert battle.team1_turn()
    assert len(battle.deck1.hand) == 5
    battle.end_turn()
    # Team 2 turn 2: place energy in Bulbasaur, card is drawn
    assert not battle.team1_turn()
    assert len(battle.deck2.hand) == 5
    assert battle.place_energy(0)
    assert battle.deck2.active[0].energies.size_of(EnergyType.GRASS) == 1
    battle.end_turn()
    # Team 1 turn 3: place energy on active, play Bulbasaur to bench, retreat, evolve bench
    assert battle.place_energy(0)
    assert battle.play_basic(3)
    assert battle.retreat(1, EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert battle.evolve(0, 1)
    battle.end_turn()
    # Team 2 turn 4: place energy on active, attack
    assert battle.place_energy(0)
    assert battle.attack(0)
    # Team 1 turn 5: place energy 1 on bench
    assert battle.deck1.active[0].hp() == 30
    assert battle.place_energy(1)
    battle.end_turn()
    # Team 2 turn 6: attack
    assert battle.attack(0)
    # Team 1 turn 6: replace starter
    assert not battle.team1_turn()
    assert battle.team2_points == 1
    assert battle.team1_move()
    assert battle.available_actions() == ['select', 'new_active']
    assert battle.select(1)
    # Team 1 turn 7: place energy 2
    assert battle.team1_turn()
    assert battle.place_energy(0)
    battle.end_turn()
    # Team 2 turn 8: attack
    assert battle.attack(0)
    # Team 1 turn 9: place energy 3 and attack
    assert battle.place_energy(0)
    assert battle.attack(0)
    # Team 2 turn 10: attack
    assert battle.attack(0)
    # Team 1 turn 11: attack, win
    assert battle.attack(0)
    assert battle.team1_points == 1
    assert battle.deck2.bench_size() == 0
    assert battle.deck2.active[0] is None
    assert battle.is_over()
    assert battle.available_actions() == []

# END OF FULL BATTLE TESTING
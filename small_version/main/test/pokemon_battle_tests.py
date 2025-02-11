from pokemon.pokemon_battle import ActivePokemon, DeckSetup, Deck, Action, Battle, Rules, battle_factory, standard_actions, standard_effects, standard_damage_effects
from pokemon.pokemon_types import Condition, EnergyContainer, EnergyType
from pokemon.pokemon_card import PokemonCard, PlayingCard, Trainer
from pokemon.pokemon_collections import generate_attacks, generate_pokemon, generate_pokemon_cards, generate_trainers, generate_abilities

from frozendict import frozendict
import pytest

# TESTING FOR ActivePokemon
def get_cards() -> dict[str, PlayingCard]:
    abilities = generate_abilities()
    attacks = generate_attacks()
    pokemon = generate_pokemon()
    trainers = generate_trainers()
    pokemon_cards = generate_pokemon_cards(pokemon, attacks, abilities)
    cards = dict[PlayingCard]()
    for name,trainer in trainers.items():
        cards[name] = trainer
    for name,pokemon_card in pokemon_cards.items():
        cards[name] = pokemon_card
    return cards

def get_bulbasaur(cards:dict[str, PokemonCard]):
    return ActivePokemon([cards['Bulbasaur 0']])

def get_ivysaur(cards:dict[str, PokemonCard]):
    return ActivePokemon([cards['Ivysaur 0'], cards['Bulbasaur 0']])

def test_default():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    assert active.turns_in_active == 0
    assert active.damage == 0
    assert active.conditions == []
    assert isinstance(active.energies, EnergyContainer)

def test_evolve():
    cards  = get_cards()
    active = get_bulbasaur(cards)

    active.turns_in_active = 1
    active.evolve(cards['Ivysaur 0'])
    assert active.active_card() == cards['Ivysaur 0']
    assert active.turns_in_active == 0

    active.evolve(cards['Venusaur ex 0'])
    assert active.active_card() == cards['Venusaur ex 0']

def test_hp():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    assert active.hp() == 70
    active.damage = 50
    assert active.hp() == 20
    active.damage = 70
    assert active.hp() == 0
    active.damage = 100
    assert active.hp() == 0

def test_end_turn():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    active.turns_in_active = 0
    active.end_turn()
    assert active.turns_in_active == 1

def test_between_turns():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    active.between_turns()
    pass

def test_attach_energy():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    active.attach_energy(EnergyType.GRASS)
    assert active.energies.size() == 1
    active.attach_energy(EnergyType.GRASS)
    assert active.energies.size() == 2

def test_retreat():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    
    active.attach_energy(EnergyType.GRASS)
    active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert active.energies.size() == 0

    with pytest.raises(Exception):
        active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))

    active.attach_energy(EnergyType.GRASS)
    active.attach_energy(EnergyType.FIRE)
    active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert active.energies.size() == 1
    assert active.energies.size_of(EnergyType.FIRE) == 1

    with pytest.raises(Exception):
        active.retreat(EnergyContainer(frozendict({EnergyType.METAL:1})))

def test_take_damage():
    cards  = get_cards()
    active = get_bulbasaur(cards)

    active.take_damage(10, EnergyType.FIRE, True)
    assert active.hp() == 40

    active.take_damage(10, EnergyType.FIRE, False)
    assert active.hp() == 30

    active.take_damage(10, EnergyType.GRASS, True)
    assert active.hp() == 20

    active.take_damage(100, EnergyType.GRASS, True)
    assert active.hp() == 0

def test_knocked_out():
    cards  = get_cards()
    active = get_bulbasaur(cards)

    assert not active.is_knocked_out()

    active.take_damage(100, EnergyType.GRASS, True)
    assert active.is_knocked_out()

    active = get_bulbasaur(cards)

    active.take_damage(70, EnergyType.GRASS, True)
    assert active.is_knocked_out()
# END OF TESTING FOR ActivePokemon


# TESTING FOR DeckSetup
def get_deck():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Charmander 0'],
        cards['Charmeleon 0'],
        cards['Charizard 0'],
        cards['Charmander 0'],
        cards['Charmeleon 0'],
        cards['Charizard 0']
    ]
    return Deck("name", deck_cards, (EnergyType.GRASS,EnergyType.FIRE))

def place_basic(deck:DeckSetup) -> bool:
    for card in deck.hand:
        if card.is_basic():
            deck.hand.remove(card)
            deck.active.append(ActivePokemon([card]))
            return True
    for card in deck.deck:
        if card.is_basic():
            deck.deck.remove(card)
            deck.active.append(ActivePokemon([card]))
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
    deck_setup = DeckSetup(deck, 5, 2)
    size = len(deck.cards)

    assert len(deck_setup.next_energies) == 2
    assert len(deck_setup.hand) == 5
    assert len(deck_setup.hand) + len(deck_setup.deck) == size

def test_start_turn():
    deck = get_deck()
    deck_setup = DeckSetup(deck, 5, 1)
    # no energy
    deck_setup.start_turn(False)
    assert len(deck_setup.next_energies) == 1
    assert len(deck_setup.hand) - 1 == 5
    # yes energy
    deck_setup = DeckSetup(deck, 5, 1)
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == 1
    assert len(deck_setup.hand) - 1 == 5

def test_between_turns():
    pass

def test_end_turn():
    pass

def test_play_card_from_hand():
    deck = get_deck()
    deck_setup = DeckSetup(deck, 5, 1)
    deck_setup.play_card_from_hand(0)
    assert same_cards(deck.cards, deck_setup)
    assert len(deck_setup.hand) == 5 - 1
    assert len(deck_setup.discard) == 1

def test_evolve():
    # TO TEST: figure out where error checking for evolving should go
    deck = get_deck()
    deck_setup = DeckSetup(deck, 5, 1)

    place_basic(deck_setup)
    place_evolution_in_hand(deck_setup, 0, 0)
    pass

# END OF TESTING FOR DeckSetup

# FULL BATTLE TESTING
def deterministic_battle_setup(deck_cards:list[PokemonCard]) -> Battle:
    deck = Deck("name1", deck_cards, (EnergyType.GRASS,))
    rules = Rules(standard_actions(), standard_effects(), standard_damage_effects(), SHUFFLE=False, DUPLICATE_LIMIT=3, DECK_SIZE=len(deck.cards))
    return battle_factory(deck, deck, rules)

def test_battle():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0']
    ]
    battle = deterministic_battle_setup(deck_cards)
    assert battle.state.rules.MAX_HAND_SIZE == 10
    assert len(battle.state.deck2.hand) == 5
    # setup: both teams place Bulbasuar to active
    assert battle.action('setup', (True, 0,))
    assert battle.action('setup', (False, 0,))
    assert len(battle.state.deck2.hand) == 4
    # Team 1 turn 1: card is drawn
    assert battle.team1_turn()
    assert len(battle.state.deck1.hand) == 5
    assert battle.action('end_turn', tuple())
    # Team 2 turn 2: place energy in Bulbasaur, card is drawn
    assert not battle.team1_turn()
    assert len(battle.state.deck2.hand) == 5
    assert battle.action('place_energy', (0,))
    assert battle.state.deck2.active[0].energies.size_of(EnergyType.GRASS) == 1
    assert battle.action('end_turn', tuple())
    # Team 1 turn 3: place energy on active, play Bulbasaur to bench, retreat, evolve bench
    assert battle.team1_turn()
    assert battle.action('place_energy', (0,))
    assert battle.action('play_basic', (3,))
    assert battle.action('retreat', (1, EnergyContainer(frozendict({EnergyType.GRASS:1}))))
    assert battle.action('evolve', (0, 1))
    assert battle.action('end_turn', tuple())
    # Team 2 turn 4: place energy on active, attack
    assert not battle.team1_turn()
    assert battle.action('place_energy', (0,))
    assert battle.action('attack', (0,))
    # Team 1 turn 5: place energy 1 on bench
    actions = list(battle.available_actions().keys())
    actions.sort()
    assert actions == ['end_turn', 'evolve', 'place_energy']
    assert battle.team1_turn()
    assert battle.state.deck1.active[0].hp() == 30
    assert battle.action('place_energy', (1,))
    assert battle.action('end_turn', tuple())
    # Team 2 turn 6: attack
    assert not battle.team1_turn()
    assert battle.action('attack', (0,))
    # Team 1 turn 6: replace starter
    assert not battle.team1_turn()
    assert battle.team1_move()
    assert battle.state.team2_points == 1
    assert battle.team1_move()
    assert list(battle.available_actions().keys()) == ['select_active']
    assert battle.action('select_active', (1,))
    # Team 1 turn 7: place energy 2
    assert battle.team1_turn()
    assert battle.action('place_energy', (0,))
    assert battle.action('end_turn', tuple())
    # Team 2 turn 8: attack
    assert not battle.team1_turn()
    assert not battle.team1_move()
    assert battle.action('attack', (0,))
    # Team 1 turn 9: place energy 3 and attack
    assert battle.team1_turn()
    assert battle.action('place_energy', (0,))
    assert battle.action('attack', (0,))
    # Team 2 turn 10: attack
    assert not battle.team1_turn()
    assert battle.action('attack', (0,))
    # Team 1 turn 11: attack, win
    assert battle.team1_turn()
    assert battle.action('attack', (0,))
    assert battle.state.team1_points == 1
    assert battle.state.deck2.bench_size() == 0
    assert battle.state.deck2.active[0] is None
    assert battle.is_over()
    assert list(battle.available_actions().keys()) == []

def check_actions(actions:dict[str,Action], should_have:list[str]):
    action_list = list(actions.keys())
    action_list.sort()
    should_have.sort()
    return action_list == should_have

def test_battle_trainers():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Sabrina'],
        cards['Bulbasaur 0'],
        cards['Venusaur 0'],

        cards['Pokeball'],
        cards['Venusaur ex 0'],
        cards["Professor's Research"],
        cards["Professor's Research"],
        cards['Pokeball'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Sabrina'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0']
    ]
    battle = deterministic_battle_setup(deck_cards)
    assert battle.state.rules.MAX_HAND_SIZE == 10
    assert len(battle.state.deck2.hand) == 5
    
    # setup: both teams place Bulbasuar to active
    assert check_actions(battle.available_actions(), ['setup'])
    assert battle.action('setup', (True,  0))
    assert battle.action('setup', (False, 3, 0))
    assert len(battle.state.deck2.hand) == 3
    
    # Team 1 turn 1: Pokeball is drawn and used
    assert battle.team1_turn()
    assert check_actions(battle.available_actions(), ['play_basic', 'end_turn', 'trainer'])
    assert len(battle.state.deck1.hand) == 5
    assert battle.action('trainer', (4,))
    assert battle.action('end_turn', tuple())
    
    # Team 2 turn 2: place energy on active Bulbasaur, Pokeball is drawn and used
    assert not battle.team1_turn()
    assert len(battle.state.deck2.hand) == 4
    assert check_actions(battle.available_actions(), ['end_turn', 'trainer', 'place_energy'])
    assert battle.action('place_energy', (0,))
    assert battle.state.deck2.active[0].energies.size_of(EnergyType.GRASS) == 1
    assert check_actions(battle.available_actions(), ['end_turn', 'trainer', 'retreat'])
    assert battle.action('trainer', (3,))
    assert check_actions(battle.available_actions(), ['end_turn', 'play_basic', 'retreat'])
    assert battle.action('play_basic', (3,))
    assert battle.action('end_turn', tuple())
    
    # Team 1 turn 3: draw random, place energy on active, play Sabrina
    assert battle.team1_turn()
    assert battle.action('place_energy', (0,))
    assert battle.action('trainer', (1,))

    # Team 2 turn 3 move: select a new active
    assert battle.team1_turn()
    assert not battle.team1_move()
    assert check_actions(battle.available_actions(), ['select_active'])
    assert not battle.action('select_active', (0,))
    assert battle.action('select_active', (1,))

    # Team 1 finish turn 3: end_turn
    assert battle.team1_turn()
    assert battle.team1_move()
    if battle.state.deck1.hand[4] == cards['Pokeball']:
        assert battle.action('trainer', (4,))
    assert check_actions(battle.available_actions(), ['evolve', 'play_basic', 'end_turn'])
    assert battle.action('end_turn', tuple())

    assert same_cards(deck_cards, battle.state.deck1)
    assert same_cards(deck_cards, battle.state.deck2)

def test_energy_boost_damage_effect():
    cards = get_cards()
    deck_cards = [
        cards['Squirtle 0'],
        cards['Wartortle 0'],
        cards['Blastoise 0'],
        cards['Blastoise ex 0'],
        cards['Squirtle 0'],
        cards['Wartortle 0'],
        cards['Blastoise 0'],
        cards['Blastoise ex 0'],
    ]
    # fully charged
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] =   ActivePokemon([cards['Blastoise ex 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.WATER:5})))
    battle.state.defending_deck().active[0] = ActivePokemon([cards['Venusaur ex 0']])
    battle.action('attack', (1,))
    assert battle.state.current_deck().active[0].damage == 160
    assert battle.state.current_deck().active[0].hp() == 30
    assert not battle.team1_turn()
    assert battle.get_score() == (0,0)
    # no bonus
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] =   ActivePokemon([cards['Blastoise ex 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.WATER:3})))
    battle.state.defending_deck().active[0] = ActivePokemon([cards['Venusaur ex 0']])
    battle.action('attack', (1,))
    assert battle.state.current_deck().active[0].damage == 100
    assert battle.state.current_deck().active[0].hp() == 90
    assert not battle.team1_turn()
    assert battle.get_score() == (0,0)

def test_venusaur_heal():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0']
    ]
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] =   ActivePokemon([cards['Venusaur ex 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.GRASS:4})))
    battle.state.defending_deck().active[0] = ActivePokemon([cards['Venusaur ex 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.GRASS:4})))
    # don't increase max hp
    battle.action('attack', (1,))
    assert not battle.team1_turn()
    assert battle.state.defending_deck().active[0].hp() == 190
    assert battle.state.current_deck().active[0].hp() == 90
    # heal when damaged
    battle.action('attack', (1,))
    assert battle.team1_turn()
    assert battle.state.defending_deck().active[0].hp() == 120
    assert battle.state.current_deck().active[0].hp() == 90
    # don't error when scoring and heal partial damage
    battle.state.current_deck().active[0].damage -= 80 # to test healing 20
    battle.state.defending_deck().active[0].damage += 30
    battle.state.defending_deck().active.append(ActivePokemon([cards['Ivysaur 0']]))
    battle.action('attack', (1,))
    assert not battle.team1_move()
    assert battle.team1_turn()
    assert battle.get_score() == (2,0)
    assert battle.state.defending_deck().active[0].hp() == 190

def test_charizard_discard():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0']
    ]
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] =   ActivePokemon([cards['Charizard ex 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.FIRE:4})))
    battle.state.defending_deck().active[0] = ActivePokemon([cards['Venusaur ex 0']])
    battle.state.defending_deck().active.append(ActivePokemon([cards['Venusaur ex 0']]))
    battle.action('attack', (1,))
    assert not battle.team1_move()
    assert battle.team1_turn()
    assert battle.get_score() == (2,0)
    assert battle.state.defending_deck().active[0].energies.size_of(EnergyType.FIRE) == 2 

def test_butterfree_heal():
    cards = get_cards()
    deck_cards = [
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0'],
        cards['Bulbasaur 0'],
        cards['Ivysaur 0'],
        cards['Venusaur 0'],
        cards['Venusaur ex 0']
    ]
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] = ActivePokemon([cards['Butterfree 0']], damage=10)
    battle.state.current_deck().active.append(ActivePokemon([cards['Butterfree 0']], damage=20))
    battle.state.current_deck().active.append(ActivePokemon([cards['Butterfree 0']], damage=50))
    battle.state.current_deck().active.append(ActivePokemon([cards['Butterfree 0']]))
    
    # use ability once from anywhere on bench
    assert battle.action('ability', (3,0))
    assert battle.state.current_deck().active[0].hp() == 120
    assert battle.state.current_deck().active[1].hp() == 120
    assert battle.state.current_deck().active[2].hp() == 90
    assert battle.state.current_deck().active[3].hp() == 120
    assert not battle.action('ability', (3,0))
    
    assert battle.action('ability', (2,0))
    assert battle.state.current_deck().active[0].hp() == 120
    assert battle.state.current_deck().active[1].hp() == 120
    assert battle.state.current_deck().active[2].hp() == 110
    assert battle.state.current_deck().active[3].hp() == 120
    assert not battle.action('ability', (2,0))

    assert battle.action('ability', (1,0))
    assert battle.state.current_deck().active[0].hp() == 120
    assert battle.state.current_deck().active[1].hp() == 120
    assert battle.state.current_deck().active[2].hp() == 120
    assert battle.state.current_deck().active[3].hp() == 120
    assert not battle.action('ability', (1,0))

    # can't use if conditions aren't met
    assert not battle.action('ability', (0,0))

    # test ability reset on next turn
    battle.action('end_turn', tuple())
    battle.action('end_turn', tuple())

    battle.state.current_deck().active[0].damage = 50
    assert battle.action('ability', (0,0))
    assert not battle.action('ability', (0,0))
    assert battle.action('ability', (1,0))
    assert not battle.action('ability', (1,0))
    
def test_caterpie_find():
    cards = get_cards()
    deck_cards = [
        cards['Squirtle 0'],
        cards['Wartortle 0'],
        cards['Blastoise 0'],
        cards['Blastoise ex 0'],
        cards['Squirtle 0'],
        cards['Wartortle 0'],
        cards['Blastoise 0'],
        cards['Bulbasaur 0'],
        cards['Blastoise ex 0'],
    ]
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] = ActivePokemon([cards['Caterpie 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert battle.action('attack', (0,))
    assert not battle.team1_turn()
    assert battle.state.defending_deck().hand[-1] == cards['Bulbasaur 0']

    # test with no target
    assert battle.action('end_turn', tuple())
    assert battle.action('attack', (0,))
    assert len(battle.state.defending_deck().hand) == 7

    # find non-basic
    cards = get_cards()
    deck_cards = [
        cards['Squirtle 0'],
        cards['Wartortle 0'],
        cards['Blastoise 0'],
        cards['Blastoise ex 0'],
        cards['Squirtle 0'],
        cards['Wartortle 0'],
        cards['Blastoise 0'],
        cards['Ivysaur 0'],
        cards['Blastoise ex 0'],
    ]
    battle = deterministic_battle_setup(deck_cards)
    battle.action('setup', (True,0))
    battle.action('setup', (False,0))
    battle.state.current_deck().active[0] = ActivePokemon([cards['Caterpie 0']], 0, 0, None, EnergyContainer(frozendict({EnergyType.GRASS:1})))
    battle.action('attack', (0,))
    assert battle.state.defending_deck().hand[-1] == cards['Ivysaur 0']

# END OF FULL BATTLE TESTING
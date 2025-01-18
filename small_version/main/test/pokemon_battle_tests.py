from pokemon.pokemon_battle import ActivePokemon, DeckSetup, Deck
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

def set_can_evolve_this_turn(active:ActivePokemon, can_evolve:bool) -> ActivePokemon:
    return ActivePokemon(active.pokemon_cards, can_evolve, active.damage, active.condition, active.energies)

def set_damage(active:ActivePokemon, damage:int) -> ActivePokemon:
    return ActivePokemon(active.pokemon_cards, active.can_evolve_this_turn, damage, active.condition, active.energies)

def test_default():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    assert active.can_evolve_this_turn == False
    assert active.damage == 0
    assert active.condition == Condition.NONE
    assert isinstance(active.energies, EnergyContainer)

def test_evolve():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    with pytest.raises(Exception):
        active.evolve(cards['Ivysaur'])

    active = set_can_evolve_this_turn(active, True)
    new_active = active.evolve(cards['Ivysaur'])
    assert new_active.active_card() == cards['Ivysaur']
    assert not new_active.can_evolve_this_turn
    with pytest.raises(Exception):
        active.evolve(cards['Venusaur'])

    new_active = set_can_evolve_this_turn(new_active, True)
    new_active = new_active.evolve(cards['Venusaur ex'])
    assert new_active.active_card() == cards['Venusaur ex']

def test_can_evolve():
    cards  = get_cards()
    active = get_bulbasaur(cards)
    assert not active.can_evolve(cards['Ivysaur'])

    active = set_can_evolve_this_turn(active, True)
    assert active.can_evolve(cards['Ivysaur'])
    assert not active.can_evolve(cards['Venusaur'])

    new_active = active.evolve(cards['Ivysaur'])
    new_active = set_can_evolve_this_turn(new_active, True)
    assert new_active.can_evolve(cards['Venusaur ex'])

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
    active = set_can_evolve_this_turn(active, False)
    new_active = active.end_turn()
    assert new_active.can_evolve_this_turn
    assert not active.can_evolve_this_turn

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
    # TO TEST: 0 retreat cost card
    cards  = get_cards()
    active = get_bulbasaur(cards)
    
    active = active.attach_energy(EnergyType.GRASS)
    new_active = active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert active.energies.size() == 1
    assert new_active.energies.size() == 0

    with pytest.raises(Exception):
        new_active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
        new_active.retreat(EnergyContainer(frozendict()))

    active = active.attach_energy(EnergyType.FIRE)
    new_active = active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert active.energies.size() == 2
    assert new_active.energies.size() == 1
    assert new_active.energies.size_of(EnergyType.FIRE) == 1

    with pytest.raises(Exception):
        active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1, EnergyType.FIRE:1})))
        active.retreat(EnergyContainer(frozendict({EnergyType.METAL:1})))

    active = get_ivysaur(cards)
    active = active.attach_energy(EnergyType.GRASS)
    with pytest.raises(Exception):
        active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    active = active.attach_energy(EnergyType.GRASS)
    new_active = active.retreat(EnergyContainer(frozendict({EnergyType.GRASS:2})))
    assert active.energies.size() == 2
    assert new_active.energies.size() == 0

def test_can_retreat():
    # TO TEST: 0 retreat cost card
    cards  = get_cards()
    active = get_bulbasaur(cards)
    
    assert not active.can_retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    active = active.attach_energy(EnergyType.GRASS)
    assert active.can_retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    assert not active.can_retreat(EnergyContainer(frozendict()))

    active = active.attach_energy(EnergyType.GRASS)
    active = active.attach_energy(EnergyType.FIRE)
    assert active.can_retreat(EnergyContainer(frozendict({EnergyType.FIRE:1})))
    assert not active.can_retreat(EnergyContainer(frozendict({EnergyType.GRASS:1, EnergyType.FIRE:1})))
    assert not active.can_retreat(EnergyContainer(frozendict({EnergyType.METAL:1})))

    active = get_ivysaur(cards)
    active = active.attach_energy(EnergyType.GRASS)
    assert not active.can_retreat(EnergyContainer(frozendict({EnergyType.GRASS:1})))
    active = active.attach_energy(EnergyType.GRASS)
    assert active.can_retreat(EnergyContainer(frozendict({EnergyType.GRASS:2})))

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
            deck.active.append(ActivePokemon(card))
            return True
    for card in deck.deck:
        if card.is_basic():
            deck.deck.remove(card)
            deck.active.append(ActivePokemon(card))
            return True
    return False

def place_evolution_in_hand(deck:DeckSetup, active_index:int, hand_index:int) -> bool:
    for card in deck.hand:
        if card.evolves_from(deck.active[active_index]):
            deck.hand.remove(card)
            deck.hand.insert(hand_index, card)
            return True
    for card in deck.deck:
        if card.evolves_from(deck.active[active_index]):
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

def set_can_evolve(deck:DeckSetup, active_index:int, can_evolve:bool):
    cards = deck.active[active_index].pokemon_cards
    damage = deck.active[active_index].damage
    condition = deck.active[active_index].condition
    energies = deck.active[active_index].energies
    deck.active[active_index] = ActivePokemon(cards, can_evolve, damage, condition, energies)

def place_energy(deck:DeckSetup, active_index:int, energy:EnergyType):
    cards = deck.active[active_index].pokemon_cards
    can_evolve = deck.active[active_index].can_evolve_this_turn
    damage = deck.active[active_index].damage
    condition = deck.active[active_index].condition
    energies = deck.active[active_index].energies.add_energy(energy)
    deck.active[active_index] = ActivePokemon(cards, can_evolve, damage, condition, energies)

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

    assert len(deck_setup.next_energies) == deck_setup.future_energies
    assert len(deck_setup.hand) == deck_setup.initial_hand_size
    assert len(deck_setup.hand) + len(deck_setup.deck) == size
    assert sum(1 for card in deck_setup.hand if card.is_basic()) >= 1

def test_get_energy():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    for _ in range(10):
        assert deck_setup.__get_energy() in deck.energies

def test_start_turn():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    # no energy
    deck_setup.start_turn(False)
    assert len(deck_setup.next_energies) == deck_setup.future_energies
    assert len(deck_setup.hand) - 1 == deck_setup.initial_hand_size
    # yes energy
    deck_setup = DeckSetup(deck.cards, deck.energies)
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == deck_setup.future_energies
    assert len(deck_setup.hand) - 1 == deck_setup.initial_hand_size
    # hand full
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=5, max_hand_size=5)
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == deck_setup.future_energies
    assert len(deck_setup.hand) == deck_setup.initial_hand_size
    # deck empty
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=len(deck.cards))
    deck_setup.start_turn()
    assert len(deck_setup.next_energies) - 1 == deck_setup.future_energies
    assert len(deck_setup.hand) == deck_setup.initial_hand_size

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
    assert len(deck_setup.hand) - 1 == deck_setup.initial_hand_size
    # hand full
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=5, max_hand_size=5)
    assert not deck_setup.draw_card()
    assert len(deck_setup.hand) == deck_setup.initial_hand_size
    # deck empty
    deck_setup = DeckSetup(deck.cards, deck.energies, initial_hand_size=len(deck.cards))
    assert not deck_setup.start_turn()
    assert len(deck_setup.hand) == deck_setup.initial_hand_size

def test_play_card_from_hand():
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)
    deck_setup.play_card_from_hand(0)
    assert same_cards(deck.cards, deck_setup)
    assert len(deck_setup.hand) - 1 == deck_setup.initial_hand_size
    assert len(deck_setup.discard) == 1

def test_evolve():
    # TO TEST: figure out where error checking for evolving should go
    deck = get_deck()
    deck_setup = DeckSetup(deck.cards, deck.energies)

    place_basic(deck_setup)
    place_evolution_in_hand(deck_setup, 0, 0)
    pass

# END OF TESTING FOR DeckSetup
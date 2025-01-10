from typing import Any

from pokemon_card import PokemonCard, Attack, stage_to_str
from pokemon_battle import ActivePokemon, OwnDeckView, OpponentDeckView


def visualize_attack(attack:Attack) -> None:
    print(f"{attack.name} {attack.base_damage}\n{attack.text}\nCost: {attack.energy_cost}")

def visualize_active_pokemon(pokemon:ActivePokemon) -> None:
    print(f"{pokemon.active_card().card_type} {stage_to_str(pokemon.active_card().pokemon.get_stage())} {pokemon.active_card().name()} {pokemon.hp()} HP")
    if not pokemon.active_card().is_basic():
        print(f"Evolves from {pokemon.active_card().evolves_from().name()}")
    for attack in pokemon.active_card().attacks:
        visualize_attack(attack)
    print(f"Retreat: {pokemon.active_card().retreat_cost}")

def visualize_card(card:PokemonCard) -> None:
    print(f"{card.card_type.name} {stage_to_str(card.pokemon.get_stage())} {card.name()} {card.hit_points} HP")
    if not card.is_basic():
        print(f"Evolves from {card.evolves_from().name()}")
    for attack in card.attacks:
        visualize_attack(attack)
    print(f"Retreat: {card.retreat_cost}")

def visualize_active_pokemon_quick(pokemon:ActivePokemon) -> None:
    print(f"{pokemon.active_card().card_type} {stage_to_str(pokemon.active_card().pokemon.get_stage())} {pokemon.active_card().name()} {pokemon.hp()} HP")

def visualize_card_quick(card:PokemonCard) -> None:
    print(f"{card.card_type.name} {stage_to_str(card.pokemon.get_stage())} {card.name()} {card.hit_points} HP")

def visualize_actives(active:tuple[ActivePokemon]) -> None:
    print("Active:")
    if len(active) > 0:
        visualize_active_pokemon_quick(active[0])
        print("Bench:")
        for card in active[1:]:
            visualize_active_pokemon_quick(card)
    else:
        print("Empty")

def visualize_card_list(cards:tuple[PokemonCard], type:str) -> None:
    print(f"{type}:")
    for card in cards:
        visualize_card_quick(card)

def visualize_own_deck(deck:OwnDeckView) -> None:
    visualize_actives(deck.active)
    visualize_card_list(deck.hand, "Hand")
    print(f"Deck: {deck.deck_size} cards\nNext Energies: {', '.join([energy.name for energy in deck.energy_queue])}")
    visualize_card_list(deck.discard_pile, "Discard")
    print(f"Energy Discard: {deck.energy_discard}")

def visualize_opponent_deck(deck:OpponentDeckView) -> None:
    visualize_actives(deck.active)
    print(f"Hand: {deck.hand_size}\nDeck: {deck.deck_size} cards\nNext Energies: {', '.join([energy.name for energy in deck.energy_queue])}")
    visualize_card_list(deck.discard_pile, "Discard")
    print(f"Energy Discard: {deck.energy_discard}")

def print_visualize(action:str, obj:Any):
    """Print out visualizations for objects and actions to help a user interact with the code

    :param action: A description of what should be printed
    :type action: str
    :param obj: Any relevant information to be printed
    :type obj: Any
    """
    pass
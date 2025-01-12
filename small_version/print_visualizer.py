from typing import Any

from pokemon_card import PokemonCard, Attack, stage_to_str
from pokemon_battle import ActivePokemon, OwnDeckView, OpponentDeckView

def visualize_attack(attack:Attack, indent:str="") -> None:
    print(f"{indent}{attack.name} {attack.base_damage}\n{attack.text}\nCost: {attack.energy_cost}")

def visualize_active_pokemon(pokemon:ActivePokemon, indent:str="") -> None:
    print(f"{indent}{pokemon.active_card().card_type} {stage_to_str(pokemon.active_card().pokemon.get_stage())} {pokemon.active_card().name()} {pokemon.hp()} HP")
    if not pokemon.active_card().is_basic():
        print(f"{indent}Evolves from {pokemon.active_card().evolves_from().name()}")
    i=0
    for attack in pokemon.active_card().attacks:
        visualize_attack(attack,f"{indent}[{i}]")
        i+=1
    print(f"{indent}Retreat: {pokemon.active_card().retreat_cost}")

def visualize_card(card:PokemonCard, indent:str="") -> None:
    print(f"{indent}{card.card_type.name} {stage_to_str(card.pokemon.get_stage())} {card.name()} {card.hit_points} HP")
    if not card.is_basic():
        print(f"{indent}Evolves from {card.evolves_from().name()}")
    i=0
    for attack in card.attacks:
        visualize_attack(attack, f"{indent}[{i}]")
        i+=1
    print(f"{indent}Retreat: {card.retreat_cost}")

def visualize_active_pokemon_quick(pokemon:ActivePokemon, indent:str="") -> None:
    print(f"{indent}{pokemon.active_card().card_type} {stage_to_str(pokemon.active_card().pokemon.get_stage())} {pokemon.active_card().name()} {pokemon.hp()} HP")

def visualize_card_quick(card:PokemonCard, indent:str="") -> None:
    print(f"{indent}{card.card_type.name} {stage_to_str(card.pokemon.get_stage())} {card.name()} {card.hit_points} HP")

def visualize_actives(active:tuple[ActivePokemon], indent:str="") -> None:
    print(f"{indent}Active:")
    if len(active) > 0:
        visualize_active_pokemon_quick(active[0], f"{indent}[0]")
        print(f"{indent}Bench:")
        i=1
        for card in active[1:]:
            visualize_active_pokemon_quick(card, f"{indent}[{i}]")
            i+=1
    else:
        print(f"{indent}Empty")

def visualize_card_list(cards:tuple[PokemonCard], type:str, indent:str="") -> None:
    print(f"{indent}{type}:")
    i=0
    for card in cards:
        visualize_card_quick(card, f"{indent}[{i}]")
        i+=1

def visualize_own_deck(deck:OwnDeckView, indent:str="") -> None:
    visualize_actives(deck.active, indent)
    visualize_card_list(deck.hand, "Hand", indent)
    print(f"{indent}Deck: {deck.deck_size} cards\nNext Energies: {', '.join([energy.name for energy in deck.energy_queue])}")
    visualize_card_list(deck.discard_pile, "Discard", indent)
    print(f"{indent}Energy Discard: {deck.energy_discard}")

def visualize_opponent_deck(deck:OpponentDeckView, indent:str="") -> None:
    visualize_actives(deck.active, indent)
    print(f"{indent}Hand: {deck.hand_size}\nDeck: {deck.deck_size} cards\nNext Energies: {', '.join([energy.name for energy in deck.energy_queue])}")
    visualize_card_list(deck.discard_pile, "Discard", indent)
    print(f"{indent}Energy Discard: {deck.energy_discard}")

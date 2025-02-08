from typing import Any

from pokemon.pokemon_types import EnergyContainer
from pokemon.pokemon_card import PlayingCard, PokemonCard, Trainer, Fossil, Attack, stage_to_str
from pokemon.pokemon_battle import ActivePokemon, OwnDeckView, OpponentDeckView

def visualize_energies(energy_container:EnergyContainer, indent:str="") -> None:
    print(f"{indent}",end='')
    for energy, count in energy_container.energies.items():
        print(f"{energy.name}: {count} ",end='')
    print("")

def visualize_attack(attack:Attack, indent:str="") -> None:
    if attack.text == "":
        print(f"{indent}{attack.name} {attack.base_damage()}")
    else:
        print(f"{indent}{attack.name} {attack.base_damage()}\n{indent}{attack.text}")
    visualize_energies(attack.energy_cost, f"{indent}Cost: ")

def visualize_active_pokemon(pokemon:ActivePokemon, indent:str="") -> None:
    if pokemon is None:
        print(f"{indent} None")
        return
    print(f"{indent}{pokemon.active_card().card_type.name} {stage_to_str(pokemon.active_card().pokemon.get_stage())} {pokemon.active_card().get_name()} {pokemon.hp()}/{pokemon.active_card().hit_points} HP")
    if not pokemon.active_card().is_basic():
        print(f"{indent}Evolves from {pokemon.active_card().evolves_from().name}")
    i=0
    for attack in pokemon.active_card().attacks:
        visualize_attack(attack,f"{indent}[{i}] ")
        i+=1
    print(f"{indent}Retreat: {pokemon.active_card().retreat_cost}")
    print(f"{indent}Weakness: {pokemon.active_card().get_weakness().name if pokemon.active_card().get_weakness() is not None else ""}")
    print(f"{indent}Resistance: {pokemon.active_card().get_resistance().name if pokemon.active_card().get_resistance() is not None else ""}")
    visualize_energies(pokemon.energies, f"{indent}Energy: ")

def visualize_pokemon_card(card:PokemonCard, indent:str="") -> None:
    if card is None:
        print(f"{indent} None")
        return
    print(f"{indent}{card.card_type.name} {stage_to_str(card.pokemon.get_stage())} {card.get_name()} {card.hit_points} HP")
    if not card.is_basic():
        print(f"{indent}Evolves from {card.evolves_from().name}")
    i=0
    for attack in card.attacks:
        visualize_attack(attack, f"{indent}[{i}] ")
        i+=1
    print(f"{indent}Retreat: {card.retreat_cost}")
    print(f"{indent}Weakness: {card.get_weakness().name if card.get_weakness() is not None else ""}")
    print(f"{indent}Resistance: {card.get_resistance().name if card.get_resistance() is not None else ""}")

def visualize_active_pokemon_quick(pokemon:ActivePokemon, indent:str="") -> None:
    if pokemon is None:
        print(f"{indent} None")
    else:
        print(f"{indent}{pokemon.active_card().card_type.name} {stage_to_str(pokemon.active_card().pokemon.get_stage())} {pokemon.active_card().get_name()} {pokemon.hp()} HP Energy: {", ".join([f"{energy.name} {count}" for energy,count in pokemon.get_energies().energies.items()])}")

def visualize_pokemon_card_quick(card:PokemonCard, indent:str="") -> None:
    if card is None:
        print(f"{indent} None")
    else:
        print(f"{indent}{card.card_type.name} {stage_to_str(card.pokemon.get_stage())} {card.get_name() if card is not None else "None"} {card.hit_points} HP")

def visualize_actives(active:tuple[ActivePokemon], indent:str="") -> None:
    print(f"{indent}Active:")
    if len(active) > 0:
        visualize_active_pokemon_quick(active[0], f"{indent}\t[0] ")
        print(f"{indent}Bench:")
        i=1
        for card in active[1:]:
            visualize_active_pokemon_quick(card, f"{indent}\t[{i}] ")
            i+=1
    else:
        print(f"{indent}Empty")

def visualize_trainer_quick(card:Trainer, indent:str="") -> None:
    print(f"{indent}{card.get_card_type().name} {card.get_name()}")

def visualize_fossil_quick(card:Fossil, indent:str="") -> None:
    print(f"{indent}{card.get_card_type().name} {card.get_name()} {card.hit_points} HP")

def visualize_fossil(card:Fossil, indent:str="") -> None:
    print(f"{indent}{card.get_card_type().name} {card.get_name()} {card.hit_points} HP\n{card.text}")

def visualize_trainer(card:Trainer, indent:str="") -> None:
    print(f"{indent}{card.get_card_type().name} {card.get_name()}\n{card.text}")

def visualize_card_quick(card:PlayingCard, indent:str="") -> None:
    if card.is_pokemon():
        visualize_pokemon_card_quick(card, indent)
    elif card.is_trainer():
        visualize_trainer_quick(card, indent)
    else:
        visualize_fossil_quick(card, indent)

def visualize_card(card:PlayingCard, indent:str="") -> None:
    if card.is_pokemon():
        visualize_pokemon_card(card, indent)
    elif card.is_trainer():
        visualize_trainer(card, indent)
    else:
        visualize_fossil(card, indent)

def visualize_card_list(cards:tuple[PlayingCard], type:str, indent:str="") -> None:
    print(f"{indent}{type}:")
    i=0
    for card in cards:
        visualize_card_quick(card, f"{indent}\t[{i}] ")
        i+=1

def visualize_own_deck(deck:OwnDeckView, indent:str="") -> None:
    visualize_actives(deck.active, indent)
    visualize_card_list(deck.hand, "Hand", indent)
    print(f"{indent}Deck: {deck.deck_size} cards\nNext Energies: {', '.join([energy.name for energy in deck.energy_queue])}")
    visualize_card_list(deck.discard_pile, "Discard", indent)
    visualize_energies(deck.energy_discard, f"{indent}Energy Discard: ")

def visualize_opponent_deck(deck:OpponentDeckView, indent:str="") -> None:
    visualize_actives(deck.active, indent)
    print(f"{indent}Hand: {deck.hand_size}\nDeck: {deck.deck_size} cards\nNext Energies: {', '.join([energy.name for energy in deck.energy_queue])}")
    visualize_card_list(deck.discard_pile, "Discard", indent)
    visualize_energies(deck.energy_discard, f"{indent}Energy Discard: ")

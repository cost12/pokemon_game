from dataclasses import dataclass

from pokemon_types import EnergyType, PokemonType, weakness, resistance, energy_type

class Ability:
    """Represents an ability a pokemon can have
    """

    def __init__(self, name:str, text:str, effect:str):
        self.name = name
        self.text = text
        self.effect = effect

class Attack:
    """Represents an attack by a pokemon
    """

    def __init__(self, name:str, base_damage:int, energy_cost:dict[EnergyType,int], attack_type:PokemonType, text:str='', effect:str=''):
        self.name = name
        self.base_damage = base_damage
        self.text = text
        self.effect = effect
        self.energy_cost = energy_cost
        self.attack_type = attack_type

@dataclass(frozen=True)
class Pokemon:
    """Represents a pokemon
    """
    name: str
    evolves_from: 'Pokemon'
    types: list[PokemonType]

    def get_stage(self) -> int:
        """Gets the evolution stage of the pokemon

        :return: 0 for basic, 1 for stage 1, 2 for stage 2
        :rtype: int
        """
        if self.evolves_from is None: 
            return 0
        else:
            return 1 + self.evolves_from.get_stage()

class PokemonCard:
    """Represents a pokemon card
    """
    pokemon: Pokemon
    hit_points: int
    level: int
    card_type: list[PokemonType]
    ability: list[Ability]
    attacks: list[Attack]
    retreat_cost: int

    def name(self) -> str:
        return self.pokemon.name if self.level_str() == '' else f'{self.pokemon.name} {self.level_str()}'
    
    def pokemon_name(self) -> str:
        return self.pokemon.name
    
    def evolves_from(self) -> Pokemon:
        return self.pokemon.evolves_from
    
    def is_basic(self) -> bool:
        return self.pokemon.evolves_from is None
    
    def level_str(self) -> str:
        if self.level <= 100:
            return ''
        elif self.level == 101:
            return 'x'
        elif self.level == 102:
            return 'ex'

    def get_weakness(self) -> EnergyType:
        return weakness(self.card_type)
    
    def get_resistance(self) -> EnergyType:
        return resistance(self.card_type)
    
    def get_energy_type(self) -> EnergyType:
        return energy_type(self.card_type)
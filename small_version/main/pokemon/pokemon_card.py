from dataclasses import dataclass, field
from frozendict import frozendict

from pokemon.pokemon_types import EnergyType, PokemonType, EnergyContainer, weakness, resistance, energy_type

@dataclass(frozen=True)
class Ability:
    name:str
    text:str
    effect:str

@dataclass(frozen=True)
class Attack:
    name:str
    base_damage:int
    energy_cost:EnergyContainer
    attack_type:PokemonType
    text:str=''
    effect:str=''

@dataclass(frozen=True)
class Pokemon:
    """Represents a pokemon
    """
    name: str
    evolves_from: 'Pokemon'
    types: tuple[PokemonType]

    def get_stage(self) -> int:
        """Gets the evolution stage of the pokemon

        :return: 0 for basic, 1 for stage 1, 2 for stage 2
        :rtype: int
        """
        if self.evolves_from is None: 
            return 0
        else:
            return 1 + self.evolves_from.get_stage()
        
def stage_to_str(stage:int) -> str:
    if stage == 0:
        return "basic"
    return f"stage {stage}"

@dataclass(frozen=True)
class PokemonCard:
    """Represents a pokemon card
    """
    pokemon: Pokemon
    hit_points: int
    card_type: PokemonType
    attacks: tuple[Attack]
    retreat_cost: int
    level: int = 0
    ability: tuple[Ability] = field(default_factory=tuple[Ability])

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
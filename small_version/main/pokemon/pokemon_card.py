from dataclasses import dataclass, field
from enum import Enum

from pokemon.pokemon_types import EnergyType, PokemonType, EnergyContainer, weakness, resistance, energy_type

@dataclass(frozen=True)
class Ability:
    id_str:str
    name:str
    text:str
    effects:tuple[tuple[str,tuple]]
    trigger:str

    def get_effects(self) -> tuple[tuple[str,tuple]]:
        return self.effects

@dataclass(frozen=True)
class Attack:
    id_str:str
    name:str
    damage_effect:tuple[str,tuple]
    energy_cost:EnergyContainer
    attack_type:PokemonType
    text:str=''
    effects:tuple[tuple[str,tuple]]=None

    def base_damage(self) -> int:
        return self.damage_effect[1][0]

    def get_damage_effect(self) -> tuple[str,tuple]:
        return self.damage_effect

    def get_effects(self) -> tuple[tuple[str,tuple]]|None:
        return self.effects

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

class CardType(Enum):
    POKEMON   = 0
    SUPPORTER = 1
    ITEM      = 2
    TOOL      = 3
    FOSSIL    = 4

class PlayingCard:
    def is_basic(self) -> bool:
        pass

    def is_pokemon(self) -> bool:
        pass

    def get_card_type(self) -> CardType:
        pass

    def get_name(self) -> str:
        pass

    def is_trainer(self) -> bool:
        pass

    def is_fossil(self) -> bool:
        pass

@dataclass(frozen=True)
class Trainer(PlayingCard):
    card_type:CardType
    name:str
    text:str
    effects:tuple[tuple[str,tuple]]

    def get_actions(self) -> tuple[tuple[str, tuple]]:
        return self.effects
    
    def get_card_type(self) -> CardType:
        return self.card_type
    
    def is_basic(self) -> bool:
        return False

    def is_pokemon(self) -> bool:
        return False

    def get_name(self) -> str:
        return self.name
    
    def is_trainer(self) -> bool:
        return True

    def is_fossil(self) -> bool:
        return False

@dataclass(frozen=True)
class Fossil(PlayingCard):
    name:str
    hit_points:int
    text:str
    
    def card_type(self) -> CardType:
        return CardType.FOSSIL
    
    def is_basic(self) -> bool:
        return False

    def is_pokemon(self) -> bool:
        return False

    def get_name(self) -> str:
        return self.name
    
    def is_trainer(self) -> bool:
        return False

    def is_fossil(self) -> bool:
        return True

@dataclass(frozen=True)
class PokemonCard(PlayingCard):
    """Represents a pokemon card
    """
    pokemon: Pokemon
    version: int
    hit_points: int
    pokemon_type: PokemonType
    attacks: tuple[Attack]
    retreat_cost: int
    level: int = 0
    abilities: tuple[Ability] = field(default_factory=tuple[Ability])

    def id_str(self) -> str:
        return f"{self.get_name()} {self.version}"

    def get_card_type(self) -> CardType:
        return CardType.POKEMON

    def is_pokemon(self) -> bool:
        return True
    
    def is_trainer(self) -> bool:
        return False

    def is_fossil(self) -> bool:
        return False

    def get_name(self) -> str:
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
        return weakness(self.pokemon_type)
    
    def get_resistance(self) -> EnergyType:
        return resistance(self.pokemon_type)
    
    def get_energy_type(self) -> EnergyType:
        return energy_type(self.pokemon_type)

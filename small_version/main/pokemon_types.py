from enum import Enum

class EnergyType(Enum):
    """Represents the different types of energy available
    """
    COLORLESS =  0
    FIRE      =  1
    WATER     =  2
    LIGHTNING =  3
    GRASS     =  4
    FIGHTING  =  5
    PSYCHIC   =  6
    DARKNESS  =  7
    METAL     =  8
    DRAGON    =  9
    FAIRY     = 10

class PokemonType(Enum):
    """Represents the different types a pokemon can be
    """
    NORMAL   =  0
    FIRE     =  1
    WATER    =  2
    ELECTRIC =  3
    GRASS    =  4
    FIGHTING =  5
    PSYCHIC  =  6
    DARK     =  7
    STEEL    =  8
    DRAGON   =  9
    FAIRY    = 10
    ICE      = 11
    GROUND   = 12
    FLYING   = 13
    POISON   = 14
    BUG      = 15
    ROCK     = 16
    GHOST    = 17

def energy_type(pokemon_type:PokemonType) -> EnergyType:
    if pokemon_type.value <= 10:
        return EnergyType(pokemon_type.value)
    match pokemon_type:
        case PokemonType.ICE:
            return EnergyType.WATER
        case PokemonType.GROUND | PokemonType.ROCK:
            return EnergyType.FIGHTING
        case PokemonType.FLYING:
            return EnergyType.DRAGON
        case PokemonType.PSYCHIC | PokemonType.GHOST:
            return EnergyType.PSYCHIC
        case PokemonType.BUG:
            return EnergyType.GRASS
        case PokemonType.POISON:
            return EnergyType.DARKNESS
        
def weakness(pokemon_type:PokemonType) -> EnergyType|None:
    match pokemon_type:
        case PokemonType.NORMAL | PokemonType.DRAGON:
            return None
        case PokemonType.FIRE:
            return EnergyType.WATER
        case PokemonType.WATER | PokemonType.ICE | PokemonType.FLYING:
            return EnergyType.LIGHTNING
        case PokemonType.ELECTRIC | PokemonType.POISON | PokemonType.DARK:
            return EnergyType.FIGHTING
        case PokemonType.GRASS | PokemonType.STEEL | PokemonType.BUG:
            return EnergyType.FIRE
        case PokemonType.FIGHTING:
            return EnergyType.PSYCHIC
        case PokemonType.PSYCHIC | PokemonType.GHOST:
            return EnergyType.DARKNESS
        case PokemonType.FAIRY:
            return PokemonType.STEEL
        case PokemonType.GROUND | PokemonType.ROCK:
            return PokemonType.GRASS
        
def resistance(pokemon_type:PokemonType) -> EnergyType|None:
    match pokemon_type:
        case PokemonType.NORMAL:
            return None
        
class Condition(Enum):
    """Represents a condition that a pokemon can be effected by
    """
    NONE           = 0
    POISONED       = 1
    ASLEEP         = 2
    PARALYZED      = 3
    CONFUSED       = 4
    CANT_ATTACK    = 5
    CANT_RETREAT   = 6
    REDUCED_ATTACK = 7
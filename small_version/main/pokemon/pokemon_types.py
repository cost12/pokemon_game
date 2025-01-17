from enum import Enum
from frozendict import frozendict
from dataclasses import dataclass, field

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

@dataclass(frozen=True)
class EnergyContainer:
    energies: frozendict[EnergyType,int] = field(default_factory=frozendict[EnergyType,int])

    def size(self) -> int:
        return sum(self.energies.values())
    
    def size_of(self, energy:EnergyType) -> int:
        return self.energies[energy] if energy in self.energies else 0 

    def add_energy(self, energy:EnergyType) -> 'EnergyContainer':
        """Add an energy to the container

        :param energy: The type of energy to add
        :type energy: EnergyType
        :return: The new energy container with the energy added
        :rtype: EnergyContainer
        """
        energies = dict(self.energies)
        if energy in self.energies:
            energies[energy] += 1
        else:
            energies[energy] = 1        
        return EnergyContainer(frozendict(energies))
    
    def add_energies(self, energies:'EnergyContainer') -> 'EnergyContainer':
        """Adds two energy containers together

        :param energies: The energies to add
        :type energies: EnergyContainer
        :return: The new energy container with energies from both containers
        :rtype: EnergyContainer
        """
        new_energies = dict(self.energies)
        for energy, count in energies.energies.items():
            if energy in new_energies:
                new_energies[energy] += count
            else:
                new_energies[energy] = count
        return EnergyContainer(frozendict(new_energies))

    def remove_energy(self, energy:EnergyType) -> 'EnergyContainer':
        """Remove an energy from the container

        :param energy: The type of energy to remove
        :type energy: EnergyType
        :return: The new energy container with the energy removed
        :rtype: EnergyContainer
        :raises ValueError: When there is no energy of the type specified within the container
        """
        energies = dict(self.energies)
        if self.size_of(energy) > 0:
            energies[energy] -= 1
            return EnergyContainer(frozendict(energies))
        raise ValueError
    
    def remove_energies(self, energies:'EnergyContainer') -> 'EnergyContainer':
        """Removes one energy container from another

        :param energies: The energies to remove from the container
        :type energies: EnergyContainer
        :return: The new container with the energies removed
        :rtype: EnergyContainer
        :raises ValueError: When an energy can't be removed
        """
        new_energies = dict(self.energies)
        for energy, count in energies.energies.items():
            if self.size_of(energy) >= count:
                new_energies[energy] -= count
            else:
                raise ValueError
        return EnergyContainer(frozendict(new_energies))
    
    def at_least_as_big(self, energies:'EnergyContainer', ignore_colorless:bool=True) -> bool:
        """Determines whether this EnergyContainer holds at least as many energies of each type as another

        :param energies: The EnergyContainer to compare with
        :type energies: EnergyContainer
        :param ignore_colorless: Whether colorless energies should be ignored when comparing types of energy, optional
        :type energies: bool
        :return: True if this EnergyContainer has at least as many energies of each type as energies, False otherwise
        :rtype: bool
        """
        for energy, count in energies.energies.items():
            if count > self.size_of(energy) and (not ignore_colorless or not energy == EnergyType.COLORLESS):
                return False
        return self.size() >= energies.size()
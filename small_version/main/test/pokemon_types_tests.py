from pokemon.pokemon_types import EnergyContainer, EnergyType

from frozendict import frozendict
import pytest

def test_empty_container():
    container = EnergyContainer()
    assert container.size() == 0
    assert container.size_of(EnergyType.FIRE) == 0
    assert container.size_of(EnergyType.COLORLESS) == 0
    container.add_energy(EnergyType.DARKNESS)
    assert container.size() == 0
    assert container.size_of(EnergyType.DARKNESS) == 0

def test_multi_energy():
    energies = frozendict({EnergyType.FIRE: 2, EnergyType.WATER: 1, EnergyType.GRASS: 4})
    container = EnergyContainer(energies)
    assert container.size() == 7
    assert container.size_of(EnergyType.FIRE) == 2
    assert container.size_of(EnergyType.WATER) == 1
    assert container.size_of(EnergyType.GRASS) == 4
    assert container.size_of(EnergyType.COLORLESS) == 0

def test_add_energy():
    energies = frozendict({EnergyType.FIRE: 2, EnergyType.WATER: 1, EnergyType.GRASS: 4})
    container = EnergyContainer(energies)

    new_container = container.add_energy(EnergyType.METAL)
    assert container.size_of(EnergyType.METAL) == 0
    assert new_container.size_of(EnergyType.METAL) == 1
    assert new_container.size_of(EnergyType.GRASS) == 4

def test_add_energies():
    energies1 = frozendict({EnergyType.FIRE: 2, EnergyType.WATER: 1, EnergyType.GRASS: 4})
    container1 = EnergyContainer(energies1)
    energies2 = frozendict({EnergyType.PSYCHIC: 2, EnergyType.LIGHTNING: 1, EnergyType.GRASS: 4})
    container2 = EnergyContainer(energies2)

    combine = container1.add_energies(container2)

    assert combine.size() == 14
    assert combine.size_of(EnergyType.GRASS) == 8
    assert combine.size_of(EnergyType.LIGHTNING) == 1
    assert container1.size() == 7
    assert container2.size() == 7

def test_remove_energy():
    energies = frozendict({EnergyType.FIRE: 2, EnergyType.WATER: 1, EnergyType.GRASS: 4})
    container = EnergyContainer(energies)

    new_container = container.remove_energy(EnergyType.FIRE)
    assert container.size() == 7
    assert container.size_of(EnergyType.FIRE) == 2
    assert new_container.size() == 6
    assert new_container.size_of(EnergyType.FIRE) == 1
    
    new_container = new_container.remove_energy(EnergyType.FIRE)
    assert new_container.size_of(EnergyType.FIRE) == 0
    with pytest.raises(Exception):
        new_container.remove_energy(EnergyType.FIRE)

    new_container = new_container.remove_energy(EnergyType.WATER)
    new_container = new_container.remove_energy(EnergyType.GRASS)
    new_container = new_container.remove_energy(EnergyType.GRASS)
    new_container = new_container.remove_energy(EnergyType.GRASS)
    new_container = new_container.remove_energy(EnergyType.GRASS)
    assert new_container.size() == 0
    with pytest.raises(Exception):
        new_container.remove_energy(EnergyType.FIGHTING)

def test_remove_energies():
    energies1 = frozendict({EnergyType.FIRE: 2, EnergyType.WATER: 1, EnergyType.GRASS: 4})
    container1 = EnergyContainer(energies1)
    energies2 = frozendict({EnergyType.FIRE: 1, EnergyType.GRASS: 2})
    container2 = EnergyContainer(energies2)

    new_container = container1.remove_energies(container2)

    assert container1.size() == 7
    assert container2.size() == 3
    assert new_container.size() == 4
    assert new_container.size_of(EnergyType.FIRE) == 1
    assert new_container.size_of(EnergyType.GRASS) == 2
    assert new_container.size_of(EnergyType.WATER) == 1

    with pytest.raises(Exception):
        new_container.remove_energies(container1)
    
    new_container = new_container.remove_energies(new_container)
    assert new_container.size() == 0

def test_at_least_as_big():
    energies1 = frozendict({EnergyType.FIRE: 2, EnergyType.WATER: 1, EnergyType.GRASS: 4})
    container1 = EnergyContainer(energies1)
    energies2 = frozendict({EnergyType.FIRE: 1, EnergyType.GRASS: 2})
    container2 = EnergyContainer(energies2)
    energies3 = frozendict({EnergyType.FIRE: 1, EnergyType.GRASS: 2, EnergyType.COLORLESS: 2})
    container3 = EnergyContainer(energies3)

    assert container1.at_least_as_big(container2)
    assert not container2.at_least_as_big(container1)
    assert container1.at_least_as_big(container1)

    assert container1.at_least_as_big(container3)
    assert not container2.at_least_as_big(container3)
    assert container3.at_least_as_big(container2)
    assert not container1.at_least_as_big(container3, False)
    assert not container3.at_least_as_big(container1, False)

def test_as_big_as2():
    energies1 = frozendict({EnergyType.FIRE: 1, EnergyType.GRASS: 2})
    container1 = EnergyContainer(energies1)
    energies2 = frozendict({EnergyType.FIRE: 1})
    container2 = EnergyContainer(energies2)

    assert container1.at_least_as_big(container2)
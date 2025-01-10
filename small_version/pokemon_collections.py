from pokemon_card import Attack, Pokemon, PokemonCard
from pokemon_types import PokemonType, EnergyType

def generate_attacks() -> dict[str,Attack]:
    vine_whip     = Attack('Vine Whip',      40, {EnergyType.COLORLESS:1,EnergyType.GRASS:1}, PokemonType.GRASS)
    razor_leaf    = Attack('Razor Leaf',     60, {EnergyType.COLORLESS:2,EnergyType.GRASS:1}, PokemonType.GRASS)
    giant_bloom   = Attack('Giant Bloom',    80, {EnergyType.COLORLESS:2,EnergyType.GRASS:2}, PokemonType.GRASS)
    ember         = Attack('Ember',          30, {EnergyType.FIRE: 1},                        PokemonType.FIRE)
    fire_claws    = Attack('Fire Claws',     60, {EnergyType.FIRE:1, EnergyType.COLORLESS:2}, PokemonType.FIRE)
    slash         = Attack('Slash',          60, {EnergyType.FIRE:1, EnergyType.COLORLESS:2}, PokemonType.FIRE)
    fire_spin     = Attack('Fire Spin',     150, {EnergyType.FIRE:2, EnergyType.COLORLESS:2}, PokemonType.FIRE)
    crimson_storm = Attack('Crimson Storm', 200, {EnergyType.FIRE:2, EnergyType.COLORLESS:2}, PokemonType.FIRE)
    water_gun     = Attack('Water Gun',      20, {EnergyType.WATER:1}, PokemonType.WATER)
    wave_splash   = Attack('Wave Splash',    40, {EnergyType.WATER:1,EnergyType.COLORLESS:1}, PokemonType.WATER)
    surf          = Attack('Surf',           40, {EnergyType.WATER:1,EnergyType.COLORLESS:1}, PokemonType.WATER)
    hydro_pump    = Attack('Hydro Pump',     80, {EnergyType.WATER:2,EnergyType.COLORLESS:1}, PokemonType.WATER)
    hydro_bazooka = Attack('Hydro Bazooka', 100, {EnergyType.WATER:2,EnergyType.COLORLESS:1}, PokemonType.WATER)
    attacks = {
        vine_whip.name:     vine_whip,
        razor_leaf.name:    razor_leaf,
        giant_bloom.name:   giant_bloom,
        ember.name:         ember,
        fire_claws.name:    fire_claws,
        slash.name:         slash,
        fire_spin.name:     fire_spin,
        crimson_storm.name: crimson_storm,
        water_gun.name:     water_gun,
        wave_splash.name:   wave_splash,
        surf.name:          surf,
        hydro_pump.name:    hydro_pump,
        hydro_bazooka.name: hydro_bazooka
    }
    return attacks

def generate_pokemon() -> dict[str,Pokemon]:
    bulbasaur =  Pokemon('Bulbasaur',  None,       (PokemonType.GRASS,PokemonType.POISON))
    ivysaur   =  Pokemon('Ivysaur',    bulbasaur,  (PokemonType.GRASS,PokemonType.POISON))
    venusaur  =  Pokemon('Venusaur',   ivysaur,    (PokemonType.GRASS,PokemonType.POISON))
    charmander = Pokemon('Charmander', None,       (PokemonType.FIRE))
    charmeleon = Pokemon('Charmeleon', charmander, (PokemonType.FIRE))
    charizard  = Pokemon('Charizard',  charmeleon, (PokemonType.FIRE))
    squirtle   = Pokemon('Squirtle',   None,       (PokemonType.WATER))
    wartortle  = Pokemon('Wartortle',  squirtle,   (PokemonType.WATER))
    blastoise  = Pokemon('Blastoise',  wartortle,  (PokemonType.WATER))
    pokemon = {
        bulbasaur.name:  bulbasaur,
        ivysaur.name:    ivysaur,
        venusaur.name:   venusaur,
        charmander.name: charmander,
        charmeleon.name: charmeleon,
        charizard.name:  charizard,
        squirtle.name:   squirtle,
        wartortle.name:  wartortle,
        blastoise.name:  blastoise
    }
    return pokemon

def generate_pokemon_cards(pokemon:dict[str,Pokemon], attacks:dict[str,Attack]) -> dict[str,PokemonCard]:
    bulbasaur    = PokemonCard(pokemon['Bulbasaur'],  70, PokemonType.GRASS, (attacks['Vine Whip']) ,  1)
    ivysaur      = PokemonCard(pokemon['Ivysaur'],    90, PokemonType.GRASS, (attacks['Razor Leaf']),  2)
    venusaur     = PokemonCard(pokemon['Venusaur'],  160, PokemonType.GRASS, (attacks['Giant Bloom']), 3)
    venusaur_ex  = PokemonCard(pokemon['Venusaur'],  190, PokemonType.GRASS, (attacks['Razor Leaf'], attacks['Giant Bloom']), 3, level=102)
    charmander   = PokemonCard(pokemon['Charmander'], 60, PokemonType.FIRE,  (attacks['Ember']), 1)
    charmeleon   = PokemonCard(pokemon['Charmeleon'], 90, PokemonType.FIRE,  (attacks['Fire Claws']), 2)
    charizard    = PokemonCard(pokemon['Charizard'], 150, PokemonType.FIRE,  (attacks['Fire Spin']), 2)
    charizard_ex = PokemonCard(pokemon['Charizard'], 180, PokemonType.FIRE,  (attacks['Slash'], attacks['Crimson Storm']), 2, level=102)
    squirtle     = PokemonCard(pokemon['Squirtle'],   60, PokemonType.WATER, (attacks['Water Gun']), 1)
    wartortle    = PokemonCard(pokemon['Wartortle'],  80, PokemonType.WATER, (attacks['Wave Splash']), 1)
    blastoise    = PokemonCard(pokemon['Blastoise'], 150, PokemonType.WATER, (attacks['Hydro Pump']), 3)
    blastoise_ex = PokemonCard(pokemon['Blastoise'], 180, PokemonType.WATER, (attacks['Surf'], attacks['Hydro Bazooka']), 3, level=102)
    pokemon = {
        bulbasaur.name():    bulbasaur,
        ivysaur.name():      ivysaur,
        venusaur.name():     venusaur,
        venusaur_ex.name():  venusaur_ex,
        charmander.name():   charmander,
        charmeleon.name():   charmeleon,
        charizard.name():    charizard,
        charizard_ex.name(): charizard_ex,
        squirtle.name():     squirtle,
        wartortle.name():    wartortle,
        blastoise.name():    blastoise,
        blastoise_ex.name(): blastoise_ex
    }
    return pokemon
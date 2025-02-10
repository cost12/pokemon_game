from pokemon.pokemon_card import Attack, Pokemon, PokemonCard, Trainer, CardType
from pokemon.pokemon_types import PokemonType, EnergyType, EnergyContainer

from frozendict import frozendict

def generate_attacks() -> dict[str,Attack]:
    vine_whip     = Attack('bulbasaur_1', 'Vine Whip',     ('base', (40,)),  EnergyContainer(frozendict({EnergyType.COLORLESS:1,EnergyType.GRASS:1})), PokemonType.GRASS)
    razor_leaf    = Attack('ivysaur_1',   'Razor Leaf',    ('base', (60,)),  EnergyContainer(frozendict({EnergyType.COLORLESS:2,EnergyType.GRASS:1})), PokemonType.GRASS)
    giant_bloom1  = Attack('venusaur_1',  'Giant Bloom',   ('base', (80,)),  EnergyContainer(frozendict({EnergyType.COLORLESS:2,EnergyType.GRASS:2})), PokemonType.GRASS, 'Heal 30 damage from this pokemon.', effect=('heal', (0, 30)))
    giant_bloom2  = Attack('venusaur_2',  'Giant Bloom',   ('base', (100,)), EnergyContainer(frozendict({EnergyType.COLORLESS:2,EnergyType.GRASS:2})), PokemonType.GRASS, 'Heal 30 damage from this pokemon.', effect=('heal', (0, 30)))
    ember         = Attack('charmander_1','Ember',         ('base', (30,)),  EnergyContainer(frozendict({EnergyType.FIRE:1})),                         PokemonType.FIRE,  'Discard a FIRE energy from this pokemon.', effect=('discard_energy', (True, 0, 1, EnergyType.FIRE)))
    fire_claws    = Attack('charmeleon_1','Fire Claws',    ('base', (60,)),  EnergyContainer(frozendict({EnergyType.FIRE:1, EnergyType.COLORLESS:2})), PokemonType.FIRE)
    slash         = Attack('charizard_1', 'Slash',         ('base', (60,)),  EnergyContainer(frozendict({EnergyType.FIRE:1, EnergyType.COLORLESS:2})), PokemonType.FIRE)
    fire_spin     = Attack('charizard_2', 'Fire Spin',     ('base', (150,)), EnergyContainer(frozendict({EnergyType.FIRE:2, EnergyType.COLORLESS:2})), PokemonType.FIRE,  'Discard 2 FIRE energy from this pokemon.', effect=('discard_energy', (True, 0, 2, EnergyType.FIRE)))
    crimson_storm = Attack('charizard_3', 'Crimson Storm', ('base', (200,)), EnergyContainer(frozendict({EnergyType.FIRE:2, EnergyType.COLORLESS:2})), PokemonType.FIRE,  'Discard 2 FIRE energy from this pokemon.', effect=('discard_energy', (True, 0, 2, EnergyType.FIRE)))
    water_gun     = Attack('squirtle_1',  'Water Gun',     ('base', (20,)),  EnergyContainer(frozendict({EnergyType.WATER:1})),                        PokemonType.WATER)
    wave_splash   = Attack('wartortle_1', 'Wave Splash',   ('base', (40,)),  EnergyContainer(frozendict({EnergyType.WATER:1,EnergyType.COLORLESS:1})), PokemonType.WATER)
    surf          = Attack('blastoise_1', 'Surf',          ('base', (40,)),  EnergyContainer(frozendict({EnergyType.WATER:1,EnergyType.COLORLESS:1})), PokemonType.WATER)
    hydro_pump    = Attack('blastoise_2', 'Hydro Pump',    ('energy_boost',  (80,  60, 2, EnergyType.WATER)),  EnergyContainer(frozendict({EnergyType.WATER:2,EnergyType.COLORLESS:1})), PokemonType.WATER, 'If this Pokemon has at least 2 extra WATER energy attached, this attack does 60 more damage.')
    hydro_bazooka = Attack('blastoise_3', 'Hydro Bazooka', ('energy_boost',  (100, 60, 2, EnergyType.WATER)), EnergyContainer(frozendict({EnergyType.WATER:2,EnergyType.COLORLESS:1})), PokemonType.WATER, 'If this Pokemon has at least 2 extra WATER energy attached, this attack does 60 more damage.')
    attacks = {
        vine_whip.id_str:     vine_whip,
        razor_leaf.id_str:    razor_leaf,
        giant_bloom1.id_str:  giant_bloom1,
        giant_bloom2.id_str:  giant_bloom2,
        ember.id_str:         ember,
        fire_claws.id_str:    fire_claws,
        slash.id_str:         slash,
        fire_spin.id_str:     fire_spin,
        crimson_storm.id_str: crimson_storm,
        water_gun.id_str:     water_gun,
        wave_splash.id_str:   wave_splash,
        surf.id_str:          surf,
        hydro_pump.id_str:    hydro_pump,
        hydro_bazooka.id_str: hydro_bazooka
    }
    return attacks

def generate_pokemon() -> dict[str,Pokemon]:
    bulbasaur =  Pokemon('Bulbasaur',  None,       (PokemonType.GRASS,PokemonType.POISON))
    ivysaur   =  Pokemon('Ivysaur',    bulbasaur,  (PokemonType.GRASS,PokemonType.POISON))
    venusaur  =  Pokemon('Venusaur',   ivysaur,    (PokemonType.GRASS,PokemonType.POISON))
    charmander = Pokemon('Charmander', None,       (PokemonType.FIRE,))
    charmeleon = Pokemon('Charmeleon', charmander, (PokemonType.FIRE,))
    charizard  = Pokemon('Charizard',  charmeleon, (PokemonType.FIRE,))
    squirtle   = Pokemon('Squirtle',   None,       (PokemonType.WATER,))
    wartortle  = Pokemon('Wartortle',  squirtle,   (PokemonType.WATER,))
    blastoise  = Pokemon('Blastoise',  wartortle,  (PokemonType.WATER,))
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
    bulbasaur    = PokemonCard(pokemon['Bulbasaur'],  0,  70, PokemonType.GRASS, (attacks['bulbasaur_1'],),1)
    ivysaur      = PokemonCard(pokemon['Ivysaur'],    0,  90, PokemonType.GRASS, (attacks['ivysaur_1'],),  2)
    venusaur     = PokemonCard(pokemon['Venusaur'],   0, 160, PokemonType.GRASS, (attacks['venusaur_1'],), 3)
    venusaur_ex  = PokemonCard(pokemon['Venusaur'],   0, 190, PokemonType.GRASS, (attacks['ivysaur_1'], attacks['venusaur_2']), 3, level=102)
    charmander   = PokemonCard(pokemon['Charmander'], 0,  60, PokemonType.FIRE,  (attacks['charmander_1'],), 1)
    charmeleon   = PokemonCard(pokemon['Charmeleon'], 0,  90, PokemonType.FIRE,  (attacks['charmeleon_1'],), 2)
    charizard    = PokemonCard(pokemon['Charizard'],  0, 150, PokemonType.FIRE,  (attacks['charizard_2'],),  2)
    charizard_ex = PokemonCard(pokemon['Charizard'],  0, 180, PokemonType.FIRE,  (attacks['charizard_1'], attacks['charizard_3']), 2, level=102)
    squirtle     = PokemonCard(pokemon['Squirtle'],   0,  60, PokemonType.WATER, (attacks['squirtle_1'],),  1)
    wartortle    = PokemonCard(pokemon['Wartortle'],  0,  80, PokemonType.WATER, (attacks['wartortle_1'],), 1)
    blastoise    = PokemonCard(pokemon['Blastoise'],  0, 150, PokemonType.WATER, (attacks['blastoise_2'],), 3)
    blastoise_ex = PokemonCard(pokemon['Blastoise'],  0, 180, PokemonType.WATER, (attacks['blastoise_1'], attacks['blastoise_3']), 3, level=102)
    pokemon = {
        bulbasaur.id_str():    bulbasaur,
        ivysaur.id_str():      ivysaur,
        venusaur.id_str():     venusaur,
        venusaur_ex.id_str():  venusaur_ex,
        charmander.id_str():   charmander,
        charmeleon.id_str():   charmeleon,
        charizard.id_str():    charizard,
        charizard_ex.id_str(): charizard_ex,
        squirtle.id_str():     squirtle,
        wartortle.id_str():    wartortle,
        blastoise.id_str():    blastoise,
        blastoise_ex.id_str(): blastoise_ex
    }
    return pokemon

def generate_trainers() -> dict[str,Trainer]:
    oak      = Trainer("Professor's Research", "Draw 2 cards",                                                        "draw",        (2,),    CardType.SUPPORTER)
    sabrina  = Trainer("Sabrina",              "Your opponent swaps their active pokemon with a card on their bench", "swap_active", tuple(), CardType.SUPPORTER)
    pokeball = Trainer("Pokeball",             "Put a random Basic Pokemon from your bench into your hand",           "draw_basic",  (1,),    CardType.ITEM)
    return {
        oak.name: oak,
        sabrina.name: sabrina,
        pokeball.name: pokeball
    }
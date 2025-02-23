from django.db import models

CARD_TYPES = {
    '0': 'POKEMON',
    '1': 'SUPPORTER',
    '2': 'ITEM',
    '3': 'TOOL',
    '4': 'FOSSIL',
}

ENERGY_TYPES = {
    '0':  'COLORLESS',
    '1': 'FIRE',
    '2':  'WATER',
    '3':  'LIGHTNING',
    '4':  'GRASS',
    '5': 'FIGHTING',
    '6':  'PSYCHIC',
    '7': 'DARKNESS',
    '8':  'METAL',
    '9': 'DRAGON',
    '10': 'FAIRY',
}

POKEMON_TYPES = {
    '0':  'NORMAL',
    '1': 'FIRE',
    '2':  'WATER',
    '3':  'ELECTRIC',
    '4': 'GRASS',
    '5': 'FIGHTING',
    '6': 'PSYCHIC',
    '7': 'DARK',
    '8':  'STEEL',
    '9': 'DRAGON',
    '10': 'FAIRY',
    '11':  'ICE',
    '12': 'GROUND',
    '13': 'FLYING',
    '14': 'POISON',
    '15':  'BUG',
    '16':  'ROCK',
    '17': 'GHOST',
}

class CardType(models.Model):
    card_type = models.CharField(max_length=2, choices=CARD_TYPES, unique=True)

class Condition(models.Model):
    name = models.CharField(unique=True)
    effect = models.CharField()

class EnergyType(models.Model):
    name = models.CharField(unique=True, max_length=2, choices=ENERGY_TYPES)

class PokemonType(models.Model):
    name               = models.CharField(unique=True, max_length=2, choices=POKEMON_TYPES)
    energy_type        = models.ForeignKey(EnergyType, on_delete=models.CASCADE)
    default_weakness   = models.ForeignKey(EnergyType, on_delete=models.SET_NULL, null=True, blank=True, related_name='default_weakness')
    default_resistance = models.ForeignKey(EnergyType, on_delete=models.SET_NULL, null=True, blank=True, related_name='default_resistance')

class Pokemon(models.Model):
    name          = models.CharField(unique=True)
    default_types = models.ManyToManyField(PokemonType)
    evolves_from  = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

class EnergyCost(models.Model):
    type   = models.ForeignKey(EnergyType, on_delete=models.CASCADE)
    amount = models.IntegerField()

class Weakness(models.Model):
    type   = models.ForeignKey(EnergyType, on_delete=models.CASCADE, related_name='weakness')
    amount = models.IntegerField(default=20)

class Resistance(models.Model):
    type   = models.ForeignKey(EnergyType, on_delete=models.CASCADE, related_name='resistance')
    amount = models.IntegerField(default=20)

class Effect(models.Model):
    name   = models.CharField()
    inputs = models.JSONField()

class Attack(models.Model):
    name          = models.CharField()
    damage_effect = models.ForeignKey(Effect, on_delete=models.CASCADE, related_name='damage_effect')
    energy_cost   = models.ManyToManyField(EnergyCost)
    attack_type   = models.ForeignKey(PokemonType, on_delete=models.CASCADE, related_name='attack_effect')
    effects       = models.ManyToManyField(Effect)
    attack_text   = models.TextField()

class Ability(models.Model):
    name         = models.CharField()
    text         = models.TextField()
    effects      = models.ForeignKey(Effect, on_delete=models.CASCADE, related_name='ability_effect')
    trigger      = models.CharField()

class PokemonCard(models.Model):
    pokemon      = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    version      = models.IntegerField()
    hit_points   = models.IntegerField()
    pokemon_type = models.ForeignKey(PokemonType, on_delete=models.CASCADE)
    attacks      = models.ManyToManyField(Attack)
    retreat_cost = models.IntegerField()
    level        = models.IntegerField()
    abilities    = models.ManyToManyField(Ability)

class Trainer(models.Model):
    card_type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    name      = models.CharField()
    text      = models.CharField()
    effects   = models.ManyToManyField(Effect, related_name='trainer_effect')

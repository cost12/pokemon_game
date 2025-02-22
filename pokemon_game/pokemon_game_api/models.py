from django.db import models

CARD_TYPES = {
    'P': 'POKEMON',
    'S': 'SUPPORTER',
    'I': 'ITEM',
    'T': 'TOOL',
    'F': 'FOSSIL',
}

ENERGY_TYPES = {
    'C':  'COLORLESS',
    'FR': 'FIRE',
    'W':  'WATER',
    'L':  'LIGHTNING',
    'G':  'GRASS',
    'FG': 'FIGHTING',
    'P':  'PSYCHIC',
    'DA': 'DARKNESS',
    'M':  'METAL',
    'DR': 'DRAGON',
    'FA': 'FAIRY',
}

POKEMON_TYPES = {
    'N':  'NORMAL',
    'FR': 'FIRE',
    'W':  'WATER',
    'E':  'ELECTRIC',
    'GA': 'GRASS',
    'FG': 'FIGHTING',
    'PS': 'PSYCHIC',
    'DA': 'DARK',
    'S':  'STEEL',
    'DR': 'DRAGON',
    'FA': 'FAIRY',
    'I':  'ICE',
    'GO': 'GROUND',
    'FL': 'FLYING',
    'PO': 'POISON',
    'B':  'BUG',
    'R':  'ROCK',
    'GH': 'GHOST',
}

class CardType(models.Model):
    card_type = models.CharField(max_length=2, choices=CARD_TYPES)

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

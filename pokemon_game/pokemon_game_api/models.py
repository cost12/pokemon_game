from django.db import models

LEVEL_CHOICES = {
    'n' : 'normal',
    'ex': 'ex',
    'x' : 'x',
    'gx': 'gx'
}

CONDITIONS = {
    'po': 'poisoned',
    'pa': 'paralyzed',
    'sl': 'asleep',
    'ca': 'cant attack',
    'cr': 'cant retreat'
}

class Condition(models.Model):
    name = models.CharField(unique=True)
    effect = models.CharField()

class EnergyType(models.Model):
    name = models.CharField(unique=True)

class PokemonType(models.Model):
    name               = models.CharField(unique=True)
    energy_type        = models.ForeignKey(EnergyType)
    default_weakness   = models.ForeignKey(EnergyType)
    default_resistance = models.ForeignKey(EnergyType)

class Pokemon(models.Model):
    name         = models.CharField(unique=True)
    number       = models.IntegerField(unique=True)
    height       = models.IntegerField()
    weight       = models.IntegerField()
    fact         = models.TextField()
    default_type = models.ForeignKey(PokemonType)
    evolves_from = models.ForeignKey('self', null=True, blank=True)

class EnergyCost(models.Model):
    type   = models.ForeignKey(EnergyType)
    amount = models.IntegerField()

class Weakness(models.Model):
    type   = models.ForeignKey(EnergyType)
    amount = models.IntegerField(default=20)

class Resistance(models.Model):
    type   = models.ForeignKey(EnergyType)
    amount = models.IntegerField(default=20)

class Attack(models.Model):
    name        = models.CharField()
    base_damage = models.IntegerField()
    effect      = models.CharField()
    attack_text = models.TextField()

class Ability(models.Model):
    name         = models.CharField()
    ability_text = models.TextField()

class PokemonCard(models.Model):
    pokemon      = models.ForeignKey(Pokemon)
    type         = models.ForeignKey(EnergyType)
    level        = models.CharField(choices=LEVEL_CHOICES)
    hit_points   = models.IntegerField()
    ability      = models.ForeignKey(Ability)
    attacks      = models.ManyToManyRel(Attack)
    weakness     = models.ForeignKey(Weakness)
    resistance   = models.ForeignKey(Resistance)
    retreat_cost = models.IntegerField()
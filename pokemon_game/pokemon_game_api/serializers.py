from rest_framework.serializers import ModelSerializer, CharField
from .models import Pokemon, Attack, Ability, PokemonCard, Trainer, Effect, CardType, Condition, EnergyCost, EnergyType, PokemonType

class CardTypeSerializer(ModelSerializer):
    class Meta:
        model = CardType
        fields = '__all__'

class ConditionSerializer(ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'

class EnergyCostSerializer(ModelSerializer):
    class Meta:
        model = EnergyCost
        fields = '__all__'

class EnergyTypeSerializer(ModelSerializer):
    class Meta:
        model = EnergyType
        fields = ['name']

class PokemonTypePkSerializer(ModelSerializer):
    class Meta:
        model = PokemonType
        fields = ['name', 'energy_type', 'default_weakness', 'default_resistance']

class PokemonTypeSerializer(ModelSerializer):
    energy_type = EnergyTypeSerializer()
    default_weakness = EnergyTypeSerializer()
    default_resistance = EnergyTypeSerializer()

    class Meta:
        model = PokemonType
        fields = ['name', 'energy_type', 'default_weakness', 'default_resistance']

class PokemonSerializer(ModelSerializer):

    class Meta:
        model = Pokemon
        fields = ['name', 'default_types', 'evolves_from']

    def get_fields(self):
        fields = super(PokemonSerializer, self).get_fields()
        fields['evolves_from'] = PokemonSerializer(many=True)
        return fields

class EffectSerializer(ModelSerializer):
    class Meta:
        model = Effect
        fields = '__all__'

class AttackSerializer(ModelSerializer):
    class Meta:
        model = Attack
        fields = '__all__'

class AbilitySerializer(ModelSerializer):
    class Meta:
        model = Ability
        fields = '__all__'

class PokemonCardSerializer(ModelSerializer):
    class Meta:
        model = PokemonCard
        fields = '__all__'

class TrainerSerializer(ModelSerializer):
    class Meta:
        model = Trainer
        fields = '__all__'
from rest_framework.serializers import ModelSerializer
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

class PokemonTypeSerializer(ModelSerializer):
    class Meta:
        model = PokemonType
        fields = '__all__'

class EnergyTypeSerializer(ModelSerializer):
    class Meta:
        model = EnergyType
        fields = '__all__'

class PokemonSerializer(ModelSerializer):
    class Meta:
        model = Pokemon
        fields = '__all__'

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
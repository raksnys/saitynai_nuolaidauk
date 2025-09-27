from rest_framework import serializers
from .models import Debt, Drinking, Participation, Drinks, Locations

class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = '__all__'

class DrinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drinks
        fields = '__all__'

class LocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = '__all__'

class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = '__all__'

class DrinkingSerializer(serializers.ModelSerializer):
    participants = ParticipationSerializer(many=True, read_only=True, source='participation_set')
    location = LocationsSerializer(read_only=True)

    class Meta:
        model = Drinking
        fields = '__all__'
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Pokemon, EnergyType, PokemonType
from .serializers import PokemonSerializer, EnergyTypeSerializer, PokemonTypeSerializer, PokemonTypePkSerializer
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template import context

class EnergyTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request:HttpRequest, *args, **kwargs):
        types = EnergyType.objects
        serializer = EnergyTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    """
    def post(self, request:HttpRequest, *args, **kwargs):
        serializer = EnergyTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """
    
class PokemonTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request:HttpRequest, *args, **kwargs):
        types = PokemonType.objects
        serializer = PokemonTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    """
    def post(self, request:HttpRequest, *args, **kwargs):
        data = {'name': request.data.get('name')}
        for category in ['energy_type', 'default_weakness', 'default_resistance']:
            if category in request.data:
                data[category] = EnergyType.objects.filter(name=request.data.get(category))[0].pk
        serializer = PokemonTypePkSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """
    
class PokemonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request:HttpRequest, *args, **kwargs):
        pokemon = Pokemon.objects
        serializer = PokemonSerializer(pokemon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request:HttpRequest, *args, **kwargs):
        if 0:
            data = {
                'name': request.data.get('name'),
                'default_types': request.data.get('default_types'),
                'evolves_from': request.data.get('evolves_from'),
            }
        serializer = PokemonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
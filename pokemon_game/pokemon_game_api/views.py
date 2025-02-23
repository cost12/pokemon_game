from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Pokemon, EnergyType, PokemonType
from .serializers import PokemonSerializer, EnergyTypeSerializer, PokemonTypeSerializer
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template import context

class EnergyTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request:HttpRequest, *args, **kwargs):
        types = EnergyType.objects
        serializer = EnergyTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request:HttpRequest, *args, **kwargs):
        serializer = EnergyTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request:HttpRequest):
        try:
          type = EnergyType.objects.get(pk=request.data['pk'])
        except EnergyType.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PokemonTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request:HttpRequest, *args, **kwargs):
        types = PokemonType.objects
        serializer = PokemonTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request:HttpRequest, *args, **kwargs):
        serializer = PokemonTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
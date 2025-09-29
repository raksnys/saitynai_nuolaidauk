from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Debt, Drinking, Participation, Drinks, Locations
from .serializers import (
    DebtSerializer,
    DrinkingSerializer,
    ParticipationSerializer,
    DrinksSerializer,
    LocationsSerializer,
)

class DebtViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='list-my-debts')
    def list_my_debts(self, request):
        user = request.user
        paid_param = request.query_params.get('paid')
        if paid_param is not None:
            paid_param = True if paid_param.lower() == "true" else False
            debts = Debt.objects.filter(debtee=user, is_paid=paid_param)
        else:
            debts = Debt.objects.filter(debtee=user)
        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='list-created-debts')
    def list_created_debts(self, request):
        user = request.user
        confirmed_param = request.query_params.get('confirmed')
        if confirmed_param is not None:
            confirmed_param = True if confirmed_param.lower() == "true" else False
            debts = Debt.objects.filter(owner = user, is_confirmed=confirmed_param)
        else:
            debts = Debt.objects.filter(owner=user)
        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='mark_unpaid')
    def mark_debt_unpaid(self, request):
        user = request.user
        debt_id = request.data.get('debt_id')
        if not debt_id:
            return Response({'error': 'Missing debt ID'}, status=status.HTTP_400_BAD_REQUEST)
        debt = get_object_or_404(Debt, pk=debt_id, owner=user)
        if debt.is_paid:
            debt.is_paid = False
            debt.is_confirmed = False
            debt.save()
            return Response({'status': 'debt marked as unpaid'})
        return Response({'error': 'Debt is already unpaid'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm_debt(self, request, pk=None):
        user = request.user
        debt = get_object_or_404(Debt, pk=pk, owner=user)
        if(debt.is_paid):
            debt.is_confirmed = True
            debt.save()
            return Response({'status': 'debt confirmed'})
        return Response({'error': 'Debt is not paid yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay_debt(self, request, pk=None):
        user = request.user
        debt = get_object_or_404(Debt, pk=pk, debtee=user)
        if not debt.is_paid:
            debt.is_paid = True
            debt.save()
            return Response({'status': 'debt paid'})
        return Response({'error': 'Debt is already paid'}, status=status.HTTP_400_BAD_REQUEST)

class DrinkingViewSet(viewsets.ModelViewSet):
    queryset = Drinking.objects.all()
    serializer_class = DrinkingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='add-participant')
    def add_participant(self, request, pk=None):
        drinking = get_object_or_404(Drinking, pk=pk)
        user = request.user
        if Participation.objects.filter(drinking=drinking, user=user).exists():
            return Response({'error': 'User is already a participant'}, status=status.HTTP_400_BAD_REQUEST)
        Participation.objects.create(drinking=drinking, user=user)
        return Response({'status': 'participant added'})

class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        drinking_id = request.data.get('drinking')
        user_id = request.data.get('user')
        if not drinking_id or not user_id:
            return Response({'error': 'Missing drinking or user ID'}, status=status.HTTP_400_BAD_REQUEST)
        if Participation.objects.filter(drinking_id=drinking_id, user_id=user_id).exists():
            return Response({'error': 'User is already a participant'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class DrinksViewSet(viewsets.ModelViewSet):
    queryset = Drinks.objects.all()
    serializer_class = DrinksSerializer
    permission_classes = [IsAuthenticated]

class LocationsViewSet(viewsets.ModelViewSet):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer
    permission_classes = [IsAuthenticated]

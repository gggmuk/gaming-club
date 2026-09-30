from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Client
from .serializers import ClientSerializer

@api_view(['GET'])
def client_info_api(request, telegram_id):
    """
    API endpoint to get client info by telegram_id.
    """
    client = get_object_or_404(Client, telegram_id=telegram_id)
    serializer = ClientSerializer(client)
    return Response(serializer.data)

@api_view(['POST'])
def register_client_api(request):
    """
    API endpoint to register a new client.
    Expects: { "telegram_id": <id>, "name": <name> }
    """
    telegram_id = request.data.get('telegram_id')
    name = request.data.get('name')
    
    if not telegram_id or not name:
        return Response(
            {"error": "telegram_id and name are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if Client.objects.filter(telegram_id=telegram_id).exists():
        return Response(
            {"error": "Client already exists"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    client = Client.objects.create(
        telegram_id=telegram_id,
        name=name,
        rank='Новичок',
        bonus_points=0,
        total_hours_played=0
    )

    # Handle referral
    referral_code = request.data.get('referral_code')
    if referral_code:
        try:
            referrer = Client.objects.get(referral_code=referral_code)
            if referrer.telegram_id != telegram_id:
                client.referred_by = referrer
                client.save()
                # Optional: Give bonus to referrer
                referrer.bonus_points += 100
                referrer.save()
        except Client.DoesNotExist:
            pass  # Invalid code, ignore
    
    serializer = ClientSerializer(client)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def apply_referral_api(request):
    """
    Apply referral code for an existing client.
    Expects: { "telegram_id": <id>, "referral_code": <code> }
    """
    telegram_id = request.data.get('telegram_id')
    referral_code = request.data.get('referral_code')
    
    client = get_object_or_404(Client, telegram_id=telegram_id)
    
    if client.referred_by:
        return Response({"error": "Already referred"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        referrer = Client.objects.get(referral_code=referral_code)
        if referrer.id == client.id:
            return Response({"error": "Cannot refer yourself"}, status=status.HTTP_400_BAD_REQUEST)
            
        client.referred_by = referrer
        client.save()
        
        # Bonus
        referrer.bonus_points += 100
        referrer.save()
        
        return Response({"message": "Referral code applied"}, status=status.HTTP_200_OK)
    except Client.DoesNotExist:
        return Response({"error": "Invalid referral code"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def referral_stats_api(request, telegram_id):
    """
    Get referral stats for a client.
    """
    client = get_object_or_404(Client, telegram_id=telegram_id)
    referrals = client.referrals.all()
    
    data = {
        "referral_code": client.referral_code,
        "referrals_count": referrals.count(),
        "referrals": [{"name": r.name, "rank": r.rank} for r in referrals]
    }
    return Response(data)

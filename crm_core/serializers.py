from rest_framework import serializers
from .models import Place, Session, Tariff, Promotion, Booking
from loyalty.models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'telegram_id', 'name', 'rank', 'bonus_points', 'total_hours_played']

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'hourly_rate', 'description', 'is_active']

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'name', 'description', 'discount_percentage', 'is_active']

class PlaceSerializer(serializers.ModelSerializer):
    active_session = serializers.SerializerMethodField()
    current_session_id = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    tariff_info = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['id', 'name', 'status', 'place_type', 'active_session', 'current_session_id', 'client_name', 'tariff_info']

    def get_active_session(self, obj):
        if obj.status == 'occupied':
            session = Session.objects.filter(place=obj, status='active').first()
            if session:
                return {
                    'id': session.id,
                    'client_name': session.guest_name if session.is_guest else (session.client.name if session.client else 'Гость'),
                    'client_id': session.client.id if session.client else None,
                    'telegram_id': session.client.telegram_id if session.client else None,
                    'start_time': session.start_time,
                    'end_time': session.end_time,
                    'scheduled_end_time': session.scheduled_end_time,
                    'is_guest': session.is_guest,
                }
        return None

    def get_current_session_id(self, obj):
        if obj.status == 'occupied':
            session = Session.objects.filter(place=obj, status='active').first()
            return session.id if session else None
        return None

    def get_client_name(self, obj):
        if obj.status == 'occupied':
            session = Session.objects.filter(place=obj, status='active').first()
            if session:
                return session.guest_name if session.is_guest else (session.client.name if session.client else 'Гость')
        return None

    def get_tariff_info(self, obj):
        if obj.tariff:
            return {
                'name': obj.tariff.name,
                'hourly_rate': float(obj.tariff.hourly_rate),
                'description': obj.tariff.description
            }
        return None

class BookingSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source='place.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'place', 'place_name', 'start_time', 'end_time', 'status', 'created_at']

class SessionSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source='place.name', read_only=True)
    client_name = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'place', 'place_name', 'client_name', 'start_time', 'end_time',
            'scheduled_end_time', 'status', 'cost', 'is_guest', 'guest_name',
            'discount_applied', 'duration_minutes'
        ]

    def get_client_name(self, obj):
        if obj.is_guest:
            return obj.guest_name or 'Гость'
        return obj.client.name if obj.client else 'Неизвестный'

    def get_duration_minutes(self, obj):
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 1)
        return None

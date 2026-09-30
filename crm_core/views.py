from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Session, Place
from loyalty.models import Client
from .serializers import PlaceSerializer, ClientSerializer
from .services import start_session, stop_session as stop_session_service, get_place_pricing_recommendation, auto_close_expired_sessions

@api_view(['POST'])
def start_session_api(request):
    """
    API endpoint to start a session.
    Supports:
    1. Registered clients: { "telegram_id": <id>, "place_id": <id> }
    2. New clients: { "telegram_id": <id>, "client_name": <name>, "place_id": <id> }
    3. Guests (no registration): { "guest_name": <name>, "place_id": <id>, "is_guest": true }
    """
    telegram_id = request.data.get('telegram_id') or request.data.get('client_telegram_id') or request.data.get('client_id')
    place_id = request.data.get('place_id')
    client_name = request.data.get('client_name', '').strip()
    guest_name = request.data.get('guest_name', '').strip()
    is_guest = request.data.get('is_guest', False)
    promotion_id = request.data.get('promotion_id')

    if not place_id:
        return Response(
            {"error": "place_id is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        place = get_object_or_404(Place, pk=place_id)
        
        # Гостевая сессия (без регистрации)
        if is_guest or (guest_name and not telegram_id):
            if not guest_name:
                return Response(
                    {"error": "guest_name is required for guest sessions"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            session = start_session(
                client=None, 
                place=place, 
                is_guest=True, 
                guest_name=guest_name,
                duration_minutes=request.data.get('duration'),
                promotion_id=promotion_id
            )
            
            return Response({
                "session_id": session.id,
                "status": session.status,
                "place": session.place.name,
                "guest_name": guest_name,
                "is_guest": True,
                "start_time": session.start_time
            }, status=status.HTTP_201_CREATED)
        
        # Зарегистрированный клиент
        if not telegram_id:
            return Response(
                {"error": "telegram_id or guest_name is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to get existing client or create new one
        try:
            client = Client.objects.get(telegram_id=telegram_id)
        except Client.DoesNotExist:
            # If client doesn't exist, create new one
            if not client_name:
                return Response(
                    {"error": "client_name is required for new clients"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            client = Client.objects.create(
                telegram_id=telegram_id,
                name=client_name,
                rank='Новичок',
                bonus_points=0,
                total_hours_played=0
            )

        session = start_session(
            client, 
            place, 
            duration_minutes=request.data.get('duration'),
            promotion_id=promotion_id
        )

        return Response({
            "session_id": session.id,
            "status": session.status,
            "place": session.place.name,
            "client": session.client.name if session.client else None,
            "client_created": client.id,
            "start_time": session.start_time
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def stop_session(request, session_id):
    """
    API endpoint to stop a session.
    Delegates logic to crm_core.services.stop_session.
    """
    try:
        result = stop_session_service(session_id)
        
        session = result['session']
        client = result['client']
        
        return Response({
            "session_id": session.id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "cost": result['cost'],
            "client": {
                "name": client.name if client else (session.guest_name or "Гость"),
                "telegram_id": client.telegram_id if client else None,
                "bonus_points_added": result['bonus_points_added'],
                "current_bonus_points": client.bonus_points if client else 0,
                "total_hours_played": round(client.total_hours_played, 2) if client else 0
            }
        }, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def place_status_list(request):
    """
    API endpoint to get the status of all places.
    """
    # Auto-close expired sessions before fetching status
    auto_close_expired_sessions()
    
    places = Place.objects.all()
    serializer = PlaceSerializer(places, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_recommendation(request, place_id):
    """
    API endpoint to get pricing recommendation for a place.
    """
    result = get_place_pricing_recommendation(place_id)
    if "error" in result:
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    return Response(result)

@api_view(['POST'])
def prolong_session(request):
    """
    API endpoint to prolong an active session.
    Expects JSON: { "session_id": <id>, "minutes_to_add": <minutes> }
    """
    from datetime import timedelta
    
    session_id = request.data.get('session_id')
    minutes_to_add = request.data.get('minutes_to_add')
    
    if not session_id or not minutes_to_add:
        return Response(
            {"error": "session_id and minutes_to_add are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = get_object_or_404(Session, pk=session_id)
        
        # Check if session is active
        if session.status != 'active':
            return Response(
                {"error": "Session is not active"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        
        # Calculate new end time
        if session.scheduled_end_time:
            # If there was already a scheduled end time, extend it
            session.scheduled_end_time += timedelta(minutes=int(minutes_to_add))
        else:
            # If it was open-ended, set scheduled end time from now
            session.scheduled_end_time = timezone.now() + timedelta(minutes=int(minutes_to_add))
            
        session.save()
        
        return Response({
            "session_id": session.id,
            "status": "prolonged",
            "minutes_added": minutes_to_add,
            "projected_end_time": session.scheduled_end_time,
            "message": f"Session extended by {minutes_to_add} minutes"
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def manager_stats(request):
    """
    API endpoint to get manager statistics.
    Returns: total_revenue_day, occupancy_rate_current, avg_session_cost, top_performing_place_name
    Calculated based on sessions STARTED today (current shift).
    """
    from django.utils import timezone
    from django.db.models import Sum, Avg, Count, Q
    from datetime import timedelta
    from decimal import Decimal
    
    now = timezone.now()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Filter sessions started today
    daily_sessions = Session.objects.filter(
        start_time__gte=day_start
    )
    
    # 1. Total revenue (from completed sessions started today)
    total_revenue = daily_sessions.filter(status='completed').aggregate(total=Sum('cost'))['total'] or Decimal(0)
    
    # 2. Average session cost (from completed sessions started today)
    avg_cost = daily_sessions.filter(status='completed').aggregate(avg=Avg('cost'))['avg'] or Decimal(0)
    
    # 3. Occupancy Rate (Average for the day)
    total_places = Place.objects.count()
    seconds_since_start = (now - day_start).total_seconds()
    
    total_duration_seconds = 0
    for session in daily_sessions:
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds()
        else:
            duration = (now - session.start_time).total_seconds()
        total_duration_seconds += duration
    
    if total_places > 0 and seconds_since_start > 1:
        max_possible_seconds = total_places * seconds_since_start
        occupancy_rate = min((total_duration_seconds / max_possible_seconds) * 100, 100.0)
    else:
        occupancy_rate = 0
    
    # 4. Top performing place (by revenue)
    top_place = daily_sessions.filter(status='completed').values('place__name').annotate(
        revenue=Sum('cost')
    ).order_by('-revenue').first()
    
    top_place_name = top_place['place__name'] if top_place else "N/A"

    # 5. Sessions count
    total_sessions_today = daily_sessions.count()
    active_sessions = daily_sessions.filter(status='active').count()
    completed_sessions = daily_sessions.filter(status='completed').count()
    
    return Response({
        "total_revenue_day": float(total_revenue),
        "occupancy_rate_current": round(occupancy_rate, 1),
        "avg_session_cost": float(avg_cost),
        "top_performing_place_name": top_place_name,
        "total_sessions_today": total_sessions_today,
        "active_sessions": active_sessions,
        "completed_sessions": completed_sessions,
    })

@api_view(['GET'])
def clients_list(request):
    """
    API endpoint to get list of all clients.
    """
    clients = Client.objects.all()
    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tariffs_list(request):
    """
    API endpoint to get list of all active tariffs.
    """
    from .models import Tariff
    
    tariffs = Tariff.objects.filter(is_active=True).order_by('hourly_rate')
    data = [{
        'id': t.id,
        'name': t.name,
        'hourly_rate': float(t.hourly_rate),
        'description': t.description
    } for t in tariffs]
    
    return Response(data)

@api_view(['POST'])
def manage_tariffs(request):
    """
    API endpoint to create a new tariff.
    """
    from .serializers import TariffSerializer
    
    serializer = TariffSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def tariff_detail(request, pk):
    """
    API endpoint to update or delete a tariff.
    """
    from .models import Tariff
    from .serializers import TariffSerializer
    
    tariff = get_object_or_404(Tariff, pk=pk)
    
    if request.method == 'PUT':
        serializer = TariffSerializer(tariff, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        tariff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def manage_promotions(request):
    """
    API endpoint to list or create promotions.
    """
    from .models import Promotion
    from .serializers import PromotionSerializer
    
    if request.method == 'GET':
        promotions = Promotion.objects.all()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def promotion_detail(request, pk):
    """
    API endpoint to update or delete a promotion.
    """
    from .models import Promotion
    from .serializers import PromotionSerializer
    
    promotion = get_object_or_404(Promotion, pk=pk)
    
    if request.method == 'PUT':
        serializer = PromotionSerializer(promotion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        promotion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def create_booking_api(request):
    """
    API endpoint to create a booking.
    Expects: { "telegram_id": <id>, "place_id": <id>, "start_time": <iso>, "end_time": <iso> }
    """
    from .models import Booking
    from .serializers import BookingSerializer
    
    telegram_id = request.data.get('telegram_id')
    place_id = request.data.get('place_id')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    
    if not all([telegram_id, place_id, start_time, end_time]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
    client = get_object_or_404(Client, telegram_id=telegram_id)
    place = get_object_or_404(Place, pk=place_id)
    
    # Check for overlaps
    overlaps = Booking.objects.filter(
        place=place,
        status__in=['confirmed', 'pending'],
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exists()
    
    if overlaps:
        return Response({"error": "Place is already booked for this time"}, status=status.HTTP_400_BAD_REQUEST)
        
    booking = Booking.objects.create(
        client=client,
        place=place,
        start_time=start_time,
        end_time=end_time,
        status='pending'
    )
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def my_bookings_api(request, telegram_id):
    """
    Get bookings for a client.
    """
    from .models import Booking
    from .serializers import BookingSerializer
    
    client = get_object_or_404(Client, telegram_id=telegram_id)
    bookings = Booking.objects.filter(client=client).order_by('-start_time')
    
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
def cancel_booking_api(request, booking_id):
    """
    Cancel a booking.
    """
    from .models import Booking
    
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if booking.status in ['canceled', 'completed']:
        return Response({"error": "Cannot cancel this booking"}, status=status.HTTP_400_BAD_REQUEST)
    
    booking.status = 'canceled'
    booking.save()
    
    return Response({"message": "Booking canceled successfully"}, status=status.HTTP_200_OK)


# ==========================================
# EXTENDED ANALYTICS API ENDPOINTS
# ==========================================

@api_view(['GET'])
def analytics_revenue(request):
    """
    Extended revenue analytics.  
    Returns daily revenue for the last 7 and 30 days, revenue by place type, by tariff.
    """
    from django.utils import timezone
    from django.db.models import Sum, Count, Avg
    from datetime import timedelta
    from decimal import Decimal
    import json
    
    now = timezone.now()
    
    # Daily revenue for last 30 days
    daily_data = []
    for i in range(29, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_sessions = Session.objects.filter(
            status='completed',
            end_time__gte=day_start,
            end_time__lt=day_end
        )
        revenue = day_sessions.aggregate(total=Sum('cost'))['total'] or Decimal(0)
        count = day_sessions.count()
        
        daily_data.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'day_label': day_start.strftime('%d.%m'),
            'revenue': float(revenue),
            'sessions_count': count,
        })
    
    # Revenue by place type
    revenue_by_type = Session.objects.filter(
        status='completed'
    ).values('place__place_type').annotate(
        total_revenue=Sum('cost'),
        total_sessions=Count('id'),
        avg_cost=Avg('cost')
    ).order_by('-total_revenue')
    
    type_data = [{
        'place_type': item['place__place_type'] or 'Unknown',
        'total_revenue': float(item['total_revenue'] or 0),
        'total_sessions': item['total_sessions'],
        'avg_cost': float(item['avg_cost'] or 0),
    } for item in revenue_by_type]
    
    # Revenue by tariff
    revenue_by_tariff = Session.objects.filter(
        status='completed',
        place__tariff__isnull=False
    ).values('place__tariff__name').annotate(
        total_revenue=Sum('cost'),
        total_sessions=Count('id'),
    ).order_by('-total_revenue')
    
    tariff_data = [{
        'tariff_name': item['place__tariff__name'],
        'total_revenue': float(item['total_revenue'] or 0),
        'total_sessions': item['total_sessions'],
    } for item in revenue_by_tariff]
    
    # Total all-time stats
    all_time = Session.objects.filter(status='completed').aggregate(
        total_revenue=Sum('cost'),
        total_sessions=Count('id'),
        avg_session_cost=Avg('cost'),
    )
    
    return Response({
        'daily': daily_data,
        'by_place_type': type_data,
        'by_tariff': tariff_data,
        'all_time': {
            'total_revenue': float(all_time['total_revenue'] or 0),
            'total_sessions': all_time['total_sessions'] or 0,
            'avg_session_cost': float(all_time['avg_session_cost'] or 0),
        }
    })


@api_view(['GET'])
def analytics_occupancy(request):
    """
    Occupancy analytics — hourly heatmap for last 7 days.
    """
    from django.utils import timezone
    from django.db.models import Q
    from datetime import timedelta
    
    now = timezone.now()
    total_places = Place.objects.count() or 1
    
    # Hourly occupancy for last 7 days (hourly averages)
    hourly_data = []
    for hour in range(24):
        total_occupancy = 0
        days_counted = 0
        for day_offset in range(7):
            day = now - timedelta(days=day_offset)
            hour_start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            if hour_end > now:
                continue
            
            sessions_in_hour = Session.objects.filter(
                Q(start_time__lt=hour_end) &
                (Q(end_time__isnull=True) | Q(end_time__gt=hour_start))
            )
            
            occupied_seconds = 0
            for s in sessions_in_hour:
                s_start = max(s.start_time, hour_start)
                s_end = min(s.end_time or now, hour_end)
                if s_end > s_start:
                    occupied_seconds += (s_end - s_start).total_seconds()
            
            max_seconds = total_places * 3600
            occupancy_pct = min((occupied_seconds / max_seconds) * 100, 100) if max_seconds > 0 else 0
            total_occupancy += occupancy_pct
            days_counted += 1
        
        avg_occupancy = total_occupancy / days_counted if days_counted > 0 else 0
        hourly_data.append({
            'hour': hour,
            'label': f'{hour:02d}:00',
            'avg_occupancy': round(avg_occupancy, 1),
        })
    
    # Current occupancy  
    active_places = Place.objects.filter(status='occupied').count()
    current_occupancy = round((active_places / total_places) * 100, 1) if total_places > 0 else 0
    
    # Occupancy by place type
    type_stats = []
    for place_type, type_label in Place.PLACE_TYPES:
        total_of_type = Place.objects.filter(place_type=place_type).count()
        occupied_of_type = Place.objects.filter(place_type=place_type, status='occupied').count()
        pct = round((occupied_of_type / total_of_type) * 100, 1) if total_of_type > 0 else 0
        type_stats.append({
            'type': place_type,
            'label': type_label,
            'total': total_of_type,
            'occupied': occupied_of_type,
            'occupancy_pct': pct,
        })
    
    return Response({
        'hourly_heatmap': hourly_data,
        'current_occupancy': current_occupancy,
        'active_places': active_places,
        'total_places': total_places,
        'by_type': type_stats,
    })


@api_view(['GET'])
def analytics_clients(request):
    """
    Client analytics — top clients, new clients trend, rank distribution.
    """
    from django.utils import timezone
    from django.db.models import Sum, Count, Avg
    from datetime import timedelta
    
    now = timezone.now()
    
    # Top 10 clients by revenue
    top_by_revenue = Session.objects.filter(
        status='completed',
        client__isnull=False
    ).values('client__name', 'client__telegram_id', 'client__rank', 'client__bonus_points').annotate(
        total_spent=Sum('cost'),
        total_sessions=Count('id'),
    ).order_by('-total_spent')[:10]
    
    top_clients = [{
        'name': c['client__name'],
        'telegram_id': c['client__telegram_id'],
        'rank': c['client__rank'],
        'bonus_points': c['client__bonus_points'],
        'total_spent': float(c['total_spent'] or 0),
        'total_sessions': c['total_sessions'],
    } for c in top_by_revenue]
    
    # Rank distribution
    rank_dist = Client.objects.values('rank').annotate(count=Count('id')).order_by('-count')
    rank_distribution = [{
        'rank': r['rank'],
        'count': r['count'],
    } for r in rank_dist]
    
    # Total clients
    total_clients = Client.objects.count()
    
    # Clients with referrals
    clients_with_referrals = Client.objects.filter(referrals__isnull=False).distinct().count()
    
    # Average bonus points
    avg_bonus = Client.objects.aggregate(avg=Avg('bonus_points'))['avg'] or 0
    
    return Response({
        'top_clients': top_clients,
        'rank_distribution': rank_distribution,
        'total_clients': total_clients,
        'clients_with_referrals': clients_with_referrals,
        'avg_bonus_points': round(float(avg_bonus), 0),
    })


@api_view(['GET'])
def analytics_sessions(request):
    """
    Session analytics — recent sessions, duration distribution, peak hours.
    """
    from django.utils import timezone
    from django.db.models import Avg, Count, Sum
    from datetime import timedelta
    from .serializers import SessionSerializer
    
    now = timezone.now()
    
    # Recent 20 completed sessions
    recent_sessions = Session.objects.filter(
        status='completed'
    ).select_related('place', 'client').order_by('-end_time')[:20]
    
    serializer = SessionSerializer(recent_sessions, many=True)
    
    # Average session duration (in minutes)
    completed = Session.objects.filter(status='completed', end_time__isnull=False)
    durations = []
    for s in completed[:100]:
        d = (s.end_time - s.start_time).total_seconds() / 60
        durations.append(d)
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Duration distribution (buckets: <30m, 30-60m, 1-2h, 2-3h, 3-5h, >5h)
    buckets = {
        '< 30 мин': 0,
        '30-60 мин': 0,
        '1-2 часа': 0,
        '2-3 часа': 0,
        '3-5 часов': 0,
        '> 5 часов': 0,
    }
    for d in durations:
        if d < 30:
            buckets['< 30 мин'] += 1
        elif d < 60:
            buckets['30-60 мин'] += 1
        elif d < 120:
            buckets['1-2 часа'] += 1
        elif d < 180:
            buckets['2-3 часа'] += 1
        elif d < 300:
            buckets['3-5 часов'] += 1
        else:
            buckets['> 5 часов'] += 1
    
    duration_distribution = [{'label': k, 'count': v} for k, v in buckets.items()]
    
    # Guest vs registered ratio
    total_completed = Session.objects.filter(status='completed').count()
    guest_sessions = Session.objects.filter(status='completed', is_guest=True).count()
    registered_sessions = total_completed - guest_sessions
    
    return Response({
        'recent_sessions': serializer.data,
        'avg_duration_minutes': round(avg_duration, 1),
        'duration_distribution': duration_distribution,
        'guest_sessions': guest_sessions,
        'registered_sessions': registered_sessions,
        'total_completed': total_completed,
    })


@api_view(['GET'])
def analytics_bookings(request):
    """
    Booking analytics.
    """
    from .models import Booking
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    
    # Booking stats
    total_bookings = Booking.objects.count()
    pending = Booking.objects.filter(status='pending').count()
    confirmed = Booking.objects.filter(status='confirmed').count()
    canceled = Booking.objects.filter(status='canceled').count()
    completed = Booking.objects.filter(status='completed').count()
    
    # Upcoming bookings (next 7 days)
    week_ahead = now + timedelta(days=7)
    upcoming = Booking.objects.filter(
        status__in=['pending', 'confirmed'],
        start_time__gte=now,
        start_time__lte=week_ahead
    ).select_related('place', 'client').order_by('start_time')[:10]
    
    upcoming_data = [{
        'id': b.id,
        'client_name': b.client.name,
        'place_name': b.place.name,
        'start_time': b.start_time,
        'end_time': b.end_time,
        'status': b.status,
    } for b in upcoming]
    
    # Most booked places
    popular_places = Booking.objects.values('place__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    popular_data = [{
        'place_name': p['place__name'],
        'booking_count': p['count'],
    } for p in popular_places]
    
    return Response({
        'total_bookings': total_bookings,
        'status_breakdown': {
            'pending': pending,
            'confirmed': confirmed,
            'canceled': canceled,
            'completed': completed,
        },
        'upcoming': upcoming_data,
        'popular_places': popular_data,
    })


@api_view(['POST'])
def confirm_booking_api(request, booking_id):
    """
    Confirm a pending booking.
    """
    from .models import Booking
    
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if booking.status != 'pending':
        return Response({"error": "Can only confirm pending bookings"}, status=status.HTTP_400_BAD_REQUEST)
    
    booking.status = 'confirmed'
    booking.save()
    
    return Response({"message": "Booking confirmed successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_bookings_list(request):
    """
    Get all bookings (for admin dashboard).
    """
    from .models import Booking
    from django.utils import timezone
    
    status_filter = request.GET.get('status', '')
    
    bookings = Booking.objects.select_related('place', 'client').order_by('-start_time')
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    data = [{
        'id': b.id,
        'client_name': b.client.name,
        'client_telegram_id': b.client.telegram_id,
        'place_name': b.place.name,
        'place_id': b.place.id,
        'start_time': b.start_time,
        'end_time': b.end_time,
        'status': b.status,
        'created_at': b.created_at,
    } for b in bookings[:50]]
    
    return Response(data)

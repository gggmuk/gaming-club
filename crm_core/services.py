from django.db import transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from .models import Session, Place, Promotion
from datetime import timedelta
import math
import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_notification(client_id, message):
    """
    Sends a notification to a client via Telegram.
    """
    try:
        from loyalty.models import Client
        
        client = Client.objects.get(pk=client_id)
        telegram_id = client.telegram_id
        
        if not telegram_id:
            logger.warning(f"Client {client_id} has no telegram_id.")
            return False

        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not set in settings.")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        
        return True

    except Client.DoesNotExist:
        logger.error(f"Client with id {client_id} not found.")
        return False
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message to {telegram_id}: {e}")
        return False

@transaction.atomic
def start_session(client, place, is_guest=False, guest_name=None, duration_minutes=None, promotion_id=None):
    """
    Начинает новую сессию для клиента или гостя на указанном месте.
    
    Args:
        client: Client object (может быть None для гостей)
        place: Place object
        is_guest: bool - является ли сессия гостевой
        guest_name: str - имя гостя (опционально)
        duration_minutes: int - длительность сессии в минутах (опционально)
        promotion_id: int - ID акции (опционально)
    """
    # Блокируем выбранное место для избежания состояния гонки
    place = Place.objects.select_for_update().get(pk=place.pk)

    if place.status != 'free':
        raise ValueError(f"Место {place.name} не свободно (статус: {place.status})")

    start_time = timezone.now()
    scheduled_end_time = None
    if duration_minutes:
        scheduled_end_time = start_time + timedelta(minutes=int(duration_minutes))

    # Handle Promotion
    promotion = None
    discount_percentage = 0
    if promotion_id:
        try:
            promotion = Promotion.objects.get(pk=promotion_id, is_active=True)
            discount_percentage = promotion.discount_percentage
        except Promotion.DoesNotExist:
            pass # Ignore invalid promotion IDs

    # Создаем новую сессию
    session = Session.objects.create(
        client=client if not is_guest else None,
        place=place,
        start_time=start_time,
        scheduled_end_time=scheduled_end_time,
        status='active',
        cost=0,
        is_guest=is_guest,
        guest_name=guest_name if is_guest else None,
        promotion=promotion,
        discount_applied=discount_percentage
    )

    # Обновляем статус места
    place.status = 'occupied'
    place.save()

    return session

@transaction.atomic
def stop_session(session_id):
    """
    Завершает активную сессию, рассчитывает стоимость и обновляет статистику клиента.
    Также отправляет уведомление в Telegram (только для зарегистрированных клиентов).
    """
    try:
        session = Session.objects.select_for_update().get(pk=session_id)
    except Session.DoesNotExist:
        raise ValueError(f"Сессия с ID {session_id} не найдена")

    if session.status == 'completed':
        raise ValueError("Сессия уже завершена")

    # 1. Устанавливаем время окончания
    now = timezone.now()
    session.end_time = now

    # 2. Рассчитываем длительность и стоимость
    duration = session.end_time - session.start_time
    hours_played_exact = Decimal(duration.total_seconds()) / Decimal(3600)
    
    hours_to_charge = Decimal(math.ceil(hours_played_exact))
    if hours_to_charge == 0:
        hours_to_charge = Decimal(1)  # Минимальная оплата за час

    # Используем тариф места или дефолтную цену
    if session.place.tariff:
        hourly_rate = session.place.tariff.hourly_rate
    else:
        hourly_rate = Decimal(300)  # Дефолтная цена
        
    cost = hours_to_charge * hourly_rate
    
    # Apply Discount
    if session.discount_applied > 0:
        discount_factor = Decimal(1) - (Decimal(session.discount_applied) / Decimal(100))
        cost = cost * discount_factor

    session.cost = cost
    session.status = 'completed'

    # 3. Освобождаем место
    place = session.place
    place.status = 'free'
    place.save()

    session.save()

    bonus_points_added = 0
    client = session.client

    # 4. Обновляем статистику клиента (только для зарегистрированных)
    if not session.is_guest and client:
        client.total_hours_played += hours_played_exact
        
        # Начисление бонусов (1%)
        bonus_points_added = int(cost * Decimal(0.01))
        client.bonus_points += bonus_points_added
        client.save()

        # 5. Отправка уведомления (только для зарегистрированных)
        try:
            msg = (
                f"✅ *Сессия завершена*\\n"
                f"📍 Место: {place.name}\\n"
                f"💰 Стоимость: {cost}₽\\n"
                f"🎁 Начислено бонусов: {bonus_points_added}\\n"
                f"💳 Ваш баланс: {client.bonus_points}"
            )
            send_telegram_notification(client.id, msg)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    return {
        "session": session,
        "cost": cost,
        "bonus_points_added": bonus_points_added,
        "client": client
    }

def get_place_pricing_recommendation(place_id):
    """
    Analyzes recent sessions for a place and recommends pricing adjustments.
    
    Logic:
    - Get last 10 sessions.
    - Calculate occupancy rate for the last 3 hours.
    - If occupancy < 30% -> Recommend -15% discount.
    - If occupancy > 80% -> Recommend +10% price increase.
    - Else -> No change.
    """
    from django.db.models import Q
    
    try:
        place = Place.objects.get(pk=place_id)
    except Place.DoesNotExist:
        return {"error": "Place not found"}

    now = timezone.now()
    three_hours_ago = now - timedelta(hours=3)
    
    # Find sessions that overlap with the last 3 hours
    recent_sessions = Session.objects.filter(
        Q(place=place) &
        Q(start_time__lt=now) &
        (Q(end_time__isnull=True) | Q(end_time__gt=three_hours_ago))
    ).order_by('-start_time')[:10]
    
    # Calculate occupancy duration in seconds within the [three_hours_ago, now] window
    total_occupied_seconds = 0
    window_start = three_hours_ago
    window_end = now
    
    for session in recent_sessions:
        # Determine overlap start
        s_start = max(session.start_time, window_start)
        # Determine overlap end
        if session.end_time:
            s_end = min(session.end_time, window_end)
        else:
            s_end = window_end  # Still active
            
        if s_end > s_start:
            total_occupied_seconds += (s_end - s_start).total_seconds()
            
    total_window_seconds = 3 * 3600
    occupancy_rate = total_occupied_seconds / total_window_seconds if total_window_seconds > 0 else 0
    
    recommendation = {
        "place_id": place.id,
        "place_name": place.name,
        "occupancy_rate_last_3h": round(occupancy_rate * 100, 1),
        "recommended_price_change": "0%",
        "insight_text": "Спрос стабильный. Изменений цены не требуется."
    }
    
    if occupancy_rate < 0.30:
        recommendation["recommended_price_change"] = "-15%"
        recommendation["insight_text"] = "Низкая загрузка (<30%). Рекомендуется снизить цену для привлечения клиентов."
    elif occupancy_rate > 0.80:
        recommendation["recommended_price_change"] = "+10%"
        recommendation["insight_text"] = "Высокая загрузка (>80%). Можно повысить цену для увеличения выручки."
        
    return recommendation

def auto_close_expired_sessions():
    """
    Checks for active sessions that have passed their end_time and closes them.
    This function is intended to be called periodically or before fetching place status.
    """
    now = timezone.now()
    expired_sessions = Session.objects.filter(
        status='active',
        scheduled_end_time__lte=now
    )
    
    count = 0
    for session in expired_sessions:
        try:
            stop_session(session.id)
            count += 1
            logger.info(f"Auto-closed expired session {session.id} for place {session.place.name}")
        except Exception as e:
            logger.error(f"Failed to auto-close session {session.id}: {e}")
            
    return count

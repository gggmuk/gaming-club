import requests
import logging
from django.conf import settings
from .models import Client

# Ensure you add TELEGRAM_BOT_TOKEN to your settings.py
# or replace this with your token string directly for testing.
TELEGRAM_BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', '8409485327:AAGpGRUFxb9z829Gwt11geK0khdFV12uxfw')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

logger = logging.getLogger(__name__)

def send_telegram_notification(client_id, message):
    """
    Sends a notification to a client via Telegram.

    Args:
        client_id: The database ID of the Client.
        message: The text message to send.
    
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    try:
        client = Client.objects.get(pk=client_id)
        telegram_id = client.telegram_id
        
        if not telegram_id:
            logger.warning(f"Client {client_id} has no telegram_id.")
            return False

        payload = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=5)
        response.raise_for_status()
        
        return True

    except Client.DoesNotExist:
        logger.error(f"Client with id {client_id} not found.")
        return False
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message to {telegram_id}: {e}")
        return False

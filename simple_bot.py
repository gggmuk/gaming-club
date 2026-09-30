import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Вставьте сюда ваш токен
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Настройки LLM API
LLM_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
LLM_API_KEY = "YOUR_LLM_API_KEY_HERE"

# Настройки Django API
DJANGO_API_BASE_URL = "http://127.0.0.1:8000/api"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def ai_sense(user_text: str) -> str:
    """
    Отправляет текст пользователя в LLM API и возвращает ответ.
    """
    headers = {
        "Content-Type": "application/json"
    }
    # Пример payload для Gemini API (может отличаться для других API)
    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }
    
    # Добавляем ключ в URL query params для Gemini
    url = f"{LLM_API_URL}?key={LLM_API_KEY}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Парсинг ответа Gemini
                    try:
                        return data['candidates'][0]['content']['parts'][0]['text']
                    except (KeyError, IndexError):
                        return "Не удалось разобрать ответ от AI."
                else:
                    logging.error(f"LLM API Error: {response.status} - {await response.text()}")
                    return "Извините, сейчас я не могу ответить. Попробуйте позже."
        except Exception as e:
            logging.error(f"Connection Error: {e}")
            return "Произошла ошибка связи с AI."

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    """
    await message.answer("Привет! Я бот для системы лояльности. Напиши мне что-нибудь, и я отвечу с помощью AI.")

@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    """
    Обработчик команды /balance. Запрашивает данные клиента из Django API.
    """
    telegram_id = message.from_user.id
    api_url = f"{DJANGO_API_BASE_URL}/client_info/{telegram_id}/"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Ожидаем: {'name': '...', 'rank': '...', 'bonus_points': 100}
                    name = data.get('name', 'Игрок')
                    rank = data.get('rank', 'Новичок')
                    points = data.get('bonus_points', 0)
                    
                    response_text = (
                        f"💳 *Баланс Клиента*\n\n"
                        f"👤 *Имя:* {name}\n"
                        f"🏆 *Ранг:* {rank}\n"
                        f"💰 *Бонусы:* `{points}`"
                    )
                    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)
                elif response.status == 404:
                    await message.answer("❌ Вы не зарегистрированы в системе лояльности.")
                else:
                    await message.answer("⚠️ Не удалось получить данные. Попробуйте позже.")
        except Exception as e:
            logging.error(f"API Error: {e}")
            await message.answer("🔌 Ошибка соединения с сервером.")

@dp.message()
async def handle_message(message: types.Message):
    """
    Обработчик всех текстовых сообщений
    """
    if not message.text:
        return

    # Отправляем действие "печатает..."
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Получаем ответ от AI
    ai_response = await ai_sense(message.text)
    
    # Отправляем ответ пользователю
    await message.answer(ai_response)

async def main():
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

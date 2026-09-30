# 🚀 Руководство по развёртыванию Gaming Club

## 📋 Требования

- Python 3.10+
- Node.js 18+
- Docker (опционально)
- PostgreSQL (опционально, по умолчанию SQLite)

---

## 🐍 Backend (Django)

### Локальная разработка

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск
python manage.py runserver
```

### Docker

```bash
# Сборка и запуск
docker-compose up -d

# Миграции
docker-compose exec backend python manage.py migrate

# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

---

## 🤖 Telegram Bot

### Локальная разработка

```bash
cd tg_bot

# Установка зависимостей
npm install

# Настройка
cp .env.example .env
# Отредактируйте .env и добавьте BOT_TOKEN

# Запуск
node index.js
```

### Docker

```bash
docker-compose up -d bot
```

---

## 📱 Mini App

### Локальная разработка

```bash
cd tg_mini_app

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

### Сборка и развёртывание на Firebase

```bash
# Сборка
npm run build

# Развёртывание
npm run deploy
```

---

## 🌐 Production

### Railway

1. Создайте проект на [Railway](https://railway.app)
2. Подключите GitHub репозиторий
3. Настройте переменные окружения:
   - `DEBUG=False`
   - `SECRET_KEY=<your-secret-key>`
   - `ALLOWED_HOSTS=<your-domain>`
   - `BOT_TOKEN=<your-bot-token>`

### Render

1. Создайте Web Service на [Render](https://render.com)
2. Подключите GitHub репозиторий
3. Настройте переменные окружения

### VPS

```bash
# Клонирование
git clone https://github.com/gggmuk/gaming-club.git
cd gaming-club

# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Bot
cd tg_bot
npm install
pm2 start index.js --name "gaming-club-bot"

# Mini App
cd ../tg_mini_app
npm install
npm run build
# Разместите dist/ на вашем веб-сервере
```

---

## 🔐 Переменные окружения

| Переменная | Описание | Обязательно |
|------------|----------|-------------|
| `DEBUG` | Режим отладки | Да |
| `SECRET_KEY` | Секретный ключ Django | Да |
| `ALLOWED_HOSTS` | Разрешённые хосты | Да |
| `BOT_TOKEN` | Токен Telegram бота | Да |
| `DATABASE_URL` | URL базы данных | Нет |
| `REDIS_URL` | URL Redis | Нет |

---

## 📊 Мониторинг

- **Backend:** Django Admin `/admin/`
- **Bot:** Логи в консоли
- **Mini App:** Firebase Console

---

## 🔄 CI/CD

Проект настроен для автоматического тестирования через GitHub Actions:

- Python тесты (pytest)
- Node.js тесты
- Линтеры (flake8, eslint)
- Форматирование (black, prettier)

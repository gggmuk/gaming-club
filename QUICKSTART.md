# 🎮 Gaming Club - Quick Start Guide

## ⚡ Быстрый запуск (Windows)

Просто запустите файл `start_all.bat` - он автоматически запустит все сервисы:

- Django Backend (порт 8000)
- Telegram Bot
- Mini App Dev Server (порт 5173)

```bash
# Двойной клик на файл или в терминале:
start_all.bat
```

## 🔧 Ручной запуск

### Вариант 1: Три терминала

**Терминал 1 - Backend:**

```bash
python manage.py runserver
```

**Терминал 2 - Telegram Bot:**

```bash
cd tg_bot
node index.js
```

**Терминал 3 - Mini App:**

```bash
cd tg_mini_app
npm run dev
```

### Вариант 2: PowerShell (параллельно)

```powershell
# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python manage.py runserver"

# Bot
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd tg_bot; node index.js"

# Mini App
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd tg_mini_app; npm run dev"
```

## 📍 Доступные URL

После запуска:

- **Backend API:** http://127.0.0.1:8000/api/
- **Главная страница:** http://127.0.0.1:8000/
- **Дашборд:** http://127.0.0.1:8000/dashboard/
- **Супер-дашборд:** http://127.0.0.1:8000/super/
- **Admin:** http://127.0.0.1:8000/admin/
- **Mini App:** http://localhost:5173/

## ✅ Проверка работы

### 1. Проверка Backend

Откройте в браузере: http://127.0.0.1:8000/api/place_status/

Должен вернуться JSON с местами.

### 2. Проверка Telegram Bot

Напишите боту `/start` в Telegram.

### 3. Проверка Mini App

Откройте http://localhost:5173/ - должна загрузиться главная страница с местами.

## 🛑 Остановка сервисов

### Если запускали через start_all.bat:

Нажмите любую клавишу в окне скрипта.

### Если запускали вручную:

Нажмите `Ctrl+C` в каждом терминале.

## 🔍 Troubleshooting

### Backend не запускается

```bash
# Проверьте установку зависимостей
pip install -r requirements.txt

# Примените миграции
python manage.py migrate
```

### Bot не запускается

```bash
cd tg_bot

# Проверьте зависимости
npm install

# Проверьте .env файл
# Должен содержать: BOT_TOKEN=your_token
```

### Mini App не запускается

```bash
cd tg_mini_app

# Установите зависимости
npm install

# Попробуйте очистить кеш
npm run build
```

### Порт уже занят

```bash
# Для Windows - найти и убить процесс на порту 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Для порта 5173
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

## 📦 Первый запуск

При первом запуске выполните:

```bash
# 1. Установите Python зависимости
pip install -r requirements.txt

# 2. Примените миграции
python manage.py migrate

# 3. (Опционально) Создайте тестовые данные
python setup_tariffs.py
python setup_places.py

# 4. Установите Node.js зависимости для бота
cd tg_bot
npm install
cd ..

# 5. Установите зависимости для Mini App
cd tg_mini_app
npm install
cd ..

# 6. Настройте .env для бота
# Создайте файл tg_bot/.env с содержимым:
# BOT_TOKEN=your_telegram_bot_token

# 7. Запустите все сервисы
start_all.bat
```

## 🎯 Следующие шаги

1. **Создайте суперпользователя для админки:**

   ```bash
   python manage.py createsuperuser
   ```

2. **Настройте тарифы и места через админку:**
   http://127.0.0.1:8000/admin/

3. **Протестируйте бота:**
   Отправьте `/start` вашему боту в Telegram

4. **Откройте Mini App:**
   http://localhost:5173/

## 🚀 Готово к разработке!

Все сервисы запущены и готовы к работе. Удачи! 🎉

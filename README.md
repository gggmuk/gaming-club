# 🎮 Gaming Club — CRM Система

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=flat-square&logo=django)
![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=nodejs)
![React](https://img.shields.io/badge/React-19+-61DAFB?style=flat-square&logo=react)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase)

**Полноценная CRM-система для игрового клуба с Telegram-ботом и Mini App**

</div>

---

## 📋 О проекте

Gaming Club — это комплексная система управления игровым клубом, включающая:

- 🎮 **Web Dashboard** — управление местами, сессиями, тарифами и акциями
- 🤖 **Telegram Bot** — управление через Telegram
- 📱 **Mini App** — мобильное приложение внутри Telegram (React + Vite)
- 📊 **Аналитика** — статистика и отчёты

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                        Gaming Club                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│    │   Web    │    │ Telegram │    │   Mini   │            │
│    │ Browser  │    │   Bot    │    │   App    │            │
│    └────┬─────┘    └────┬─────┘    └────┬─────┘            │
│         │               │               │                   │
│         └───────────────┼───────────────┘                   │
│                         │                                   │
│                         ▼                                   │
│              ┌─────────────────────┐                        │
│              │   Django REST API   │                        │
│              │   (Backend Server)  │                        │
│              └──────────┬──────────┘                        │
│                         │                                   │
│                         ▼                                   │
│              ┌─────────────────────┐                        │
│              │   SQLite Database   │                        │
│              └─────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Структура проекта

```
gaming-club/
├── config/                    # Django конфигурация
│   ├── settings.py            # Настройки проекта
│   ├── urls.py                # URL маршруты
│   └── wsgi.py                # WSGI конфигурация
│
├── crm_core/                  # Основной CRM модуль
│   ├── models.py              # Модели: Place, Session, Booking, Tariff, Promotion
│   ├── views.py               # API endpoints
│   ├── serializers.py         # DRF сериализаторы
│   ├── services.py            # Бизнес-логика
│   └── migrations/            # Миграции БД
│
├── loyalty/                   # Система лояльности
│   ├── models.py              # Модель Client (с рефералами)
│   ├── views.py               # API для клиентов и рефералов
│   ├── serializers.py         # Сериализаторы клиентов
│   └── services.py            # Логика начисления бонусов
│
├── templates/                 # HTML шаблоны
│   ├── landing.html           # Главная страница
│   ├── operations_dashboard.html  # Операционный дашборд
│   └── super_dashboard.html   # Супер-дашборд (аналитика)
│
├── static/                    # Статические файлы
│   └── css/                   # Стили
│
├── tg_bot/                    # Telegram бот (Node.js)
│   ├── index.js               # Основной файл бота
│   ├── package.json           # Зависимости
│   └── .env.example           # Шаблон переменных
│
├── tg_mini_app/               # Telegram Mini App (React)
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/             # Страницы приложения
│   │   └── lib/               # API клиент
│   ├── public/                # Публичные файлы
│   ├── package.json           # Зависимости
│   ├── vite.config.js         # Vite конфигурация
│   └── firebase.json          # Firebase Hosting
│
├── manage.py                  # Django управление
├── requirements.txt           # Python зависимости
├── docker-compose.yml         # Docker оркестрация
└── README.md                  # Этот файл
```

---

## 🚀 Запуск проекта

### 1. Backend (Django)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver
```

Сервер будет доступен по адресу: `http://127.0.0.1:8000`

### 2. Telegram Bot (Node.js)

```bash
cd tg_bot

# Установка зависимостей
npm install

# Настройка .env
cp .env.example .env
# Отредактируйте .env и добавьте BOT_TOKEN

# Запуск бота
node index.js
```

### 3. Mini App (React + Vite)

```bash
cd tg_mini_app

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

Приложение будет доступно по адресу: `http://localhost:5173`

---

## 🔌 API Endpoints

### Клиенты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/client_info/<telegram_id>/` | Информация о клиенте |
| POST | `/api/register_client/` | Регистрация клиента |
| GET | `/api/clients/` | Список всех клиентов |

### Места и сессии

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/place_status/` | Статус всех мест |
| POST | `/api/start_session/` | Начать сессию |
| POST | `/api/stop_session/<session_id>/` | Остановить сессию |
| POST | `/api/prolong_session/` | Продлить сессию |

### Бронирования

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/create_booking/` | Создать бронирование |
| GET | `/api/my_bookings/<telegram_id>/` | Мои бронирования |
| PATCH | `/api/cancel_booking/<booking_id>/` | Отменить бронирование |

### Рефералы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/apply_referral/` | Применить реферальный код |
| GET | `/api/referral_stats/<telegram_id>/` | Статистика рефералов |

### Тарифы и акции

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/tariffs/` | Список тарифов |
| POST | `/api/tariffs/manage/` | Создать тариф |
| PUT | `/api/tariffs/<id>/` | Обновить тариф |
| DELETE | `/api/tariffs/<id>/` | Удалить тариф |
| GET | `/api/promotions/` | Список акций |
| POST | `/api/promotions/` | Создать акцию |

---

## 🎨 Функционал

### Web Dashboard

- 📊 Управление местами и статусами
- 📈 Аналитика и статистика
- 👥 Управление клиентами
- ⚙️ Настройка тарифов и акций

### Telegram Bot

- 👋 Приветствие пользователей
- 🎮 Проверка статуса мест
- 👤 Просмотр профиля

### Mini App

- 🎮 Просмотр свободных мест
- 📅 Бронирование мест
- 👥 Реферальная программа
- 👤 Профиль и статистика

---

## 🛠️ Технологии

### Backend

- **Django 5.2** — веб-фреймворк
- **Django REST Framework** — REST API
- **SQLite** — база данных (можно заменить на PostgreSQL)

### Telegram Bot

- **Node.js** — среда выполнения
- **node-telegram-bot-api** — Telegram API
- **Axios** — HTTP клиент

### Mini App

- **React 19** — UI библиотека
- **Vite** — сборщик
- **React Router** — маршрутизация
- **Axios** — HTTP клиент
- **Lucide React** — иконки

---

## 📱 Развёртывание Mini App на Firebase

```bash
cd tg_mini_app
npm run deploy
```

---

## 🔐 Безопасность

### Для production:

1. ✅ Смените `SECRET_KEY` в `settings.py`
2. ✅ Установите `DEBUG = False`
3. ✅ Настройте `ALLOWED_HOSTS`
4. ✅ Используйте PostgreSQL вместо SQLite
5. ✅ Настройте HTTPS
6. ✅ Ограничьте CORS только для Firebase

---

## 📄 Лицензия

MIT

---

<div align="center">

### ⭐ Если тебе нравится проект — поставь звезду!

</div>

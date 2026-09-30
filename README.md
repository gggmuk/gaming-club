# 🎮 Gaming Club — CRM Система

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=flat-square&logo=django)
![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=nodejs)
![React](https://img.shields.io/badge/React-19+-61DAFB?style=flat-square&logo=react)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase)
![Docker](https://img.shields.io/badge/Docker-24+-2496ED?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions)

**Полноценная CRM-система для игрового клуба с Telegram-ботом и Mini App**

[Демо](#демо) • [Установка](#установка) • [Документация](docs/API.md) • [Развёртывание](docs/DEPLOYMENT.md)

</div>

---

## 📋 О проекте

Gaming Club — это комплексная система управления игровым клубом, включающая:

- 🎮 **Web Dashboard** — управление местами, сессиями, тарифами и акциями
- 🤖 **Telegram Bot** — управление через Telegram
- 📱 **Mini App** — мобильное приложение внутри Telegram (React + Vite)
- 📊 **Аналитика** — статистика и отчёты

---

## 🎯 Демо

### Web Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  🎮 Gaming Club — Операционный дашборд                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ VIP Room 1  │  │ VIP Room 2  │  │ Basic PC 1  │         │
│  │ ✓ Свободно  │  │ ● Занято    │  │ ✓ Свободно  │         │
│  │ 500₽/ч     │  │ 500₽/ч     │  │ 200₽/ч     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Статистика                                       │   │
│  │ Выручка (день): 15,000₽                            │   │
│  │ Загрузка: 75%                                       │   │
│  │ Средний чек: 450₽                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Telegram Bot

```
┌─────────────────────────────────────────┐
│  🤖 Gaming Club Bot                     │
├─────────────────────────────────────────┤
│                                         │
│  👋 Привет! Я бот Gaming Club.         │
│                                         │
│  📊 Статус мест:                       │
│  • VIP Room 1 — Свободно               │
│  • VIP Room 2 — Занято                 │
│  • Basic PC 1 — Свободно               │
│                                         │
│  💳 Ваш баланс: 150 бонусов            │
│  🏆 Ваш ранг: Постоянный               │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🚀 Установка

### Быстрый старт (Docker)

```bash
git clone https://github.com/gggmuk/gaming-club.git
cd gaming-club
docker-compose up -d
```

### Ручная установка

#### Backend

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Telegram Bot

```bash
cd tg_bot
npm install
cp .env.example .env
# Отредактируйте .env и добавьте BOT_TOKEN
node index.js
```

#### Mini App

```bash
cd tg_mini_app
npm install
npm run dev
```

---

## 📚 Документация

- [API Documentation](docs/API.md) — полное описание REST API
- [Deployment Guide](docs/DEPLOYMENT.md) — руководство по развёртыванию
- [Architecture](ARCHITECTURE.md) — архитектура проекта
- [Changelog](CHANGELOG.md) — история изменений

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

### Инфраструктура
- **Docker** — контейнеризация
- **GitHub Actions** — CI/CD
- **Firebase** — хостинг Mini App

---

## 📊 Структура проекта

```
gaming-club/
├── config/                    # Django конфигурация
├── crm_core/                  # CRM модуль
├── loyalty/                   # Система лояльности
├── templates/                 # HTML шаблоны
├── static/                    # CSS/JS
├── tg_bot/                    # Telegram бот
├── tg_mini_app/               # Mini App (React)
├── tests/                     # Тесты
├── docs/                      # Документация
├── .github/workflows/         # CI/CD
├── docker-compose.yml         # Docker
├── requirements.txt           # Python зависимости
└── README.md                  # Этот файл
```

---

## ✅ Тестирование

```bash
# Python тесты
python manage.py test

# С покрытием
pytest --cov=. --cov-report=html

# Node.js тесты
cd tg_bot && npm test
cd tg_mini_app && npm test
```

---

## 🔐 Безопасность

- ✅ CSRF защита
- ✅ CORS настройки
- ✅ Валидация входных данных
- ✅ SQL injection защита (Django ORM)
- ✅ XSS защита

---

## 📈 CI/CD

Проект настроен для автоматического тестирования через GitHub Actions:

- ✅ Python тесты (pytest)
- ✅ Node.js тесты
- ✅ Линтеры (flake8, eslint)
- ✅ Форматирование (black, prettier)
- ✅ Проверка миграций

---

## 🤝 Вклад в проект

Мы приветствуем вклад в проект! Пожалуйста, ознакомьтесь с [руководством по вкладу](CONTRIBUTING.md) перед началом работы.

---

## 📄 Лицензия

Этот проект лицензирован под MIT License — см. файл [LICENSE](LICENSE) для деталей.

---

## 👨‍💻 Автор

**gggmuk** — разработчик из Кыргызстана

- GitHub: [@gggmuk](https://github.com/gggmuk)

---

<div align="center">

### ⭐ Если тебе нравится проект — поставь звезду!

</div>

# 🚀 Инструкция по деплою на Firebase Hosting

## Шаг 1: Установка Firebase CLI

Если еще не установлен, выполните:

```bash
npm install -g firebase-tools
```

## Шаг 2: Логин в Firebase

```bash
firebase login
```

Откроется браузер для авторизации через Google аккаунт.

## Шаг 3: Создание проекта в Firebase Console

1. Перейдите на [Firebase Console](https://console.firebase.google.com/)
2. Нажмите "Add project" (Добавить проект)
3. Введите название проекта (например: `gaming-club-mini-app`)
4. Отключите Google Analytics (не обязательно для хостинга)
5. Нажмите "Create project"

## Шаг 4: Инициализация Firebase в проекте

В папке `tg_mini_app` выполните:

```bash
firebase init hosting
```

Ответьте на вопросы:

- **Select a default Firebase project**: выберите созданный проект
- **What do you want to use as your public directory?**: `dist`
- **Configure as a single-page app?**: `Yes`
- **Set up automatic builds and deploys with GitHub?**: `No`
- **File dist/index.html already exists. Overwrite?**: `No`

## Шаг 5: Сборка приложения

```bash
npm run build
```

Это создаст папку `dist` с готовыми файлами.

## Шаг 6: Деплой на Firebase

```bash
firebase deploy --only hosting
```

После успешного деплоя вы получите URL вида:

```
https://your-project-id.web.app
```

## Шаг 7: Быстрый деплой (одной командой)

Используйте готовый скрипт:

```bash
npm run deploy
```

Это автоматически выполнит сборку и деплой.

## Шаг 8: Подключение к Telegram Bot

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/mybots`
3. Выберите вашего бота
4. Выберите `Bot Settings` → `Menu Button`
5. Введите:
   - **Button text**: `Открыть приложение` (или любой текст)
   - **URL**: ваш Firebase URL (например: `https://gaming-club-mini-app.web.app`)

## Шаг 9: Настройка CORS на Backend

Добавьте в Django `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# Для продакшена укажите конкретный домен
CORS_ALLOWED_ORIGINS = [
    "https://your-project-id.web.app",
    "https://your-project-id.firebaseapp.com",
]

# Или для разработки (НЕ используйте в продакшене!)
# CORS_ALLOW_ALL_ORIGINS = True
```

Установите django-cors-headers:

```bash
pip install django-cors-headers
```

## Шаг 10: Обновление API URL

В файле `src/lib/api.js` измените URL на ваш backend:

```javascript
const API_BASE_URL = "https://your-backend-domain.com/api";
```

Затем пересоберите и задеплойте:

```bash
npm run deploy
```

## 🔄 Обновление приложения

При внесении изменений просто выполните:

```bash
npm run deploy
```

## 📱 Тестирование

1. Откройте ваш Telegram бот
2. Нажмите на кнопку меню (внизу у поля ввода)
3. Приложение должно открыться в Telegram

## 🛠 Полезные команды

```bash
# Локальный просмотр собранного приложения
npm run preview

# Просмотр логов Firebase
firebase hosting:channel:list

# Удаление деплоя (осторожно!)
firebase hosting:channel:delete <channel-id>
```

## ⚠️ Важно!

- Убедитесь, что ваш backend доступен из интернета
- Настройте HTTPS для backend (обязательно для Telegram Mini Apps)
- Проверьте CORS настройки
- Для production используйте реальный домен, а не localhost

## 🎉 Готово!

Ваше мини-приложение теперь доступно в Telegram!

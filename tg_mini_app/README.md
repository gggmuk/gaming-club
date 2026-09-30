# 🎮 Telegram Mini App - Gaming Club

Мини-приложение для игрового клуба с системой бронирования и реферальной программой.
npm install -g firebase-tools
cd tg_mini_app
firebase init hosting
npm run deploy
Откройте @BotFather
/mybots → ваш бот → Bot Settings → Menu Button
Укажите URL вашего Firebase приложения
Текущее состояние:
Запущено:

✅ Django Backend (http://127.0.0.1:8000)
✅ Mini App Dev Server (http://localhost:5173)
Функционал Mini App:

🏠 Главная - список мест с кнопкой "Забронировать"
📅 Бронирования - список броней с возможностью отмены
🎁 Рефералы - реферальный код и список приглашенных
👤 Профиль - статистика (ранг, бонусы, часы, рефералы)
Все готово к тестированию и деплою! 🚀
## 🚀 Функционал

- 🏠 **Главная** - просмотр статуса игровых мест и бронирование
- 👤 **Профиль** - статистика игрока (ранг, бонусы, часы)
- 🎁 **Рефералы** - реферальная программа с бонусами
- 📅 **Бронирования** - управление своими бронями

## 🛠 Технологии

- React 18 + Vite
- React Router для навигации
- Axios для API запросов
- Lucide React для иконок

## 📦 Установка и запуск

### Локальная разработка

```bash
# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

Приложение будет доступно на `http://localhost:5173`

### Сборка для продакшена

```bash
npm run build
```

Готовые файлы будут в папке `dist/`

## 🔥 Деплой на Firebase Hosting

### 1. Установка Firebase CLI

```bash
npm install -g firebase-tools
```

### 2. Логин в Firebase

```bash
firebase login
```

### 3. Инициализация проекта (первый раз)

```bash
firebase init hosting
```

Выберите:

- Existing project или создайте новый
- Public directory: `dist`
- Single-page app: `Yes`
- GitHub deploys: `No` (опционально)

### 4. Сборка и деплой

```bash
# Сборка приложения
npm run build

# Деплой на Firebase
firebase deploy --only hosting
```

### 5. Быстрый деплой (одной командой)

Добавьте в `package.json` скрипт:

```json
"scripts": {
  "deploy": "npm run build && firebase deploy --only hosting"
}
```

Затем просто:

```bash
npm run deploy
```

## 🔗 Подключение к Telegram Bot

После деплоя:

1. Получите URL вашего приложения (например: `https://your-app.web.app`)
2. Откройте [@BotFather](https://t.me/BotFather) в Telegram
3. Отправьте `/mybots`
4. Выберите своего бота
5. Выберите `Bot Settings` → `Menu Button`
6. Настройте Web App URL на ваш Firebase URL

## ⚙️ Настройка API

В файле `src/lib/api.js` измените `API_BASE_URL` на ваш backend:

```javascript
const API_BASE_URL = "https://your-backend.com/api";
```

## 📱 Тестирование

Для локального тестирования с mock данными:

```javascript
import { setMockId } from "./lib/api";
setMockId(123456789); // Ваш тестовый Telegram ID
```

## 🎨 Кастомизация

Цвета и стили настраиваются в `src/index.css`:

```css
:root {
  --bg-color: #0f172a;
  --primary: #8b5cf6;
  --secondary: #ec4899;
  /* ... */
}
```

## 📄 Лицензия

MIT

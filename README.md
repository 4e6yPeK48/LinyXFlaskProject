# LinyX Shop (Flask)

Магазин для Minecraft‑сервера с интеграцией EasyDonate. Бекенд на Flask, фронтенд на Bootstrap + JS. Кэширование данных магазина и отложенная подзагрузка описаний товаров.

- Главная: список избранных товаров и виджеты
- Страница товаров
- Детальная карточка товара (AJAX)
- Создание платежа через EasyDonate
- Авторизация через `Flask-Login`
- Планируемая интеграция Discord‑бота 

## Стек

- Python (Flask, Flask‑Login, Flask‑SQLAlchemy, Flask‑WTF, requests, waitress)
- MySQL (`mysql-connector-python`)
- Jinja2 шаблоны (`templates/`)
- Bootstrap, jQuery, GSAP (через CDN)
- JavaScript в `static/js/*`

## Требования

- Python 3.10+
- MySQL 8.x (или совместимый)
- Доступ к EasyDonate API

## Установка

- Клонировать репозиторий.
- Создать виртуальное окружение и установить зависимости.

```bash
# Bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt || pip install flask flask_sqlalchemy flask_login flask_wtf requests waitress mysql-connector-python discord.py
```

```powershell
# PowerShell (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Конфигурация

Все секреты хранить в переменных окружения. Не коммитить ключи и токены.

Обязательные переменные:
- `SECRET_KEY` — секрет Flask
- `SQLALCHEMY_DATABASE_URI` — строка подключения к БД (`mysql+mysqlconnector://user:pass@host:3306/db`)
- `EASYDONATE_KEY` — ключ магазина EasyDonate
- `DISCORD_TOKEN` — токен бота Discord (если включать бота)
- `FLASK_DEBUG` — `0` или `1`
- Необязательно: `HOST`, `PORT` для запуска

Пример для PowerShell:
```powershell
# PowerShell
$env:SECRET_KEY = "replace_me"
$env:SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://user:pass@host:3306/dbname"
$env:EASYDONATE_KEY = "replace_me"
$env:DISCORD_TOKEN = "replace_me"
$env:FLASK_DEBUG = "1"
```

Пример для Bash:
```bash
# Bash
export SECRET_KEY="replace_me"
export SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://user:pass@host:3306/dbname"
export EASYDONATE_KEY="replace_me"
export DISCORD_TOKEN="replace_me"
export FLASK_DEBUG=1
```

Важно:
- В `app.py` сейчас есть значения-заглушки (`SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `EASYDONATE_KEY`, `discord_token`). Перенесите нужное в переменные окружения перед продакшеном.
- `server_id` для EasyDonate жестко задан как `79936` в `buy_product`; при необходимости вынести в конфиг.

## Запуск

Приложение по умолчанию стартует через `waitress`.

```bash
# Bash
python app.py --host 0.0.0.0 --port 5000
```

```powershell
# PowerShell
python .\app.py --host localhost --port 5000
```

На старте выполняется прогрев кэша продуктов и фоновая подзагрузка описаний.

Альтернатива для разработки: включить обычный `app.run` и отключить `waitress` в `__main__`.

## Основные роуты

- GET `/` — главная
- GET `/products` — список товаров
- GET `/product_info/<int:product_id>` — JSON карточки товара
- POST `/buy_product/<int:product_id>` — создание платежа EasyDonate
  - Тело: JSON `{ "username": "Игрок" }` (если не авторизован)
- GET/POST `/login` — форма входа (подтверждение заглушено)
- GET `/logout`
- GET/POST `/account` — аккаунт (требует вход)

Примечания:
- Данные магазина кэшируются (`functools.lru_cache`).
- Для JSON‑POST запросов и CSRF: при активном `CSRFProtect` защищайте эндпоинты либо передавайте токен в заголовке. При необходимости пометьте API‑маршрут исключением.

## Структура

- `app.py` — приложение Flask, интеграция EasyDonate, кэш, роуты
- `templates/` — Jinja2 шаблоны (`base.html`, `index.html`, `products.html`, и т.д.)
- `static/css/*` — стили
- `static/js/*` — фронтенд‑логика (параллакс, фильтры, AJAX, покупка)
- `forms/` — WTForms (`login.py` и др.)

## Интеграция EasyDonate

- Получение товаров: `GET https://easydonate.ru/api/v3/shop/products`
- Карточка товара: `GET https://easydonate.ru/api/v3/shop/product/<id>`
- Создание платежа: `GET https://easydonate.ru/api/v3/shop/payment/create` с параметрами
- Ключ магазина передавать в заголовке `Shop-Key`

## Discord‑бот (опционально)

Код бота находится в `app.py` и закомментирован. Для использования:
- Установить `discord.py`.
- Заполнить `DISCORD_TOKEN`.
- Разкомментировать запуск клиента и вспомогательные функции.
- Запускать параллельно с сайтом или отдельно.

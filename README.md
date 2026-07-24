# goit-pyweb-hw-13

Асинхронний Python-проєкт для отримання курсів валют ПриватБанку.

Проект містить:

* консольну утиліту для отримання курсів валют за останні 1–10 днів;
* WebSocket-чат із командами `exchange` та `exchange N`;
* Docker Compose для запуску WebSocket-сервера та HTML-сторінки.

## Можливості

### Консольна утиліта

Файл `privat_bank_currency_rates.py`:

* виконує асинхронні запити через `aiohttp`;
* паралельно отримує дані за кілька днів через `asyncio.gather`;
* показує курси `EUR` та `USD`;
* дозволяє додавати інші валюти;
* використовує курси купівлі та продажу ПриватБанку: `purchaseRate` і `saleRate`;
* обробляє помилки підключення, тайм-аути та інші мережеві помилки;
* виводить результат у форматі JSON.

### WebSocket-чат

Файл `main.py`:

* запускає WebSocket-сервер на порту `8080`;
* надсилає повідомлення всім підключеним користувачам;
* підтримує команди `exchange` та `exchange N`;
* показує курси `EUR` і `USD` за останні 1–10 днів;
* записує використання команди `exchange` у файл `log.txt`;
* використовує `aiofile` та `aiopath` для асинхронного запису логів.

## Встановлення

```bash
git clone https://github.com/Bomber99-debug/goit-pyweb-hw-13.git
cd goit-pyweb-hw-13
poetry install --no-root
```

## Консольна утиліта

Курс за поточний день:

```bash
poetry run python privat_bank_currency_rates.py
```

Курс за останні кілька днів:

```bash
poetry run python privat_bank_currency_rates.py 3
```

Допустима кількість днів: від `1` до `10`.

Додавання інших валют:

```bash
poetry run python privat_bank_currency_rates.py 3 --currencies GBP PLN CHF
```

Скорочений варіант:

```bash
poetry run python privat_bank_currency_rates.py 3 -c GBP PLN CHF
```

## Запуск через Docker

Зібрати образи та запустити контейнери:

```bash
docker compose up --build
```

Після запуску відкрийте:

```text
http://localhost:8000
```

Сервіси:

* HTML-сторінка: `http://localhost:8000`;
* WebSocket-сервер: `ws://localhost:8080`.

Зупинити контейнери:

```bash
docker compose down
```

Після змін у коді або статичних файлах потрібно повторно зібрати образи:

```bash
docker compose up --build
```

## Команди чату

Поточний курс:

```text
exchange
```

Курс за останні кілька днів:

```text
exchange 3
```

Допустиме значення: від `1` до `10`.

Інший текст надсилається як звичайне повідомлення чату.

## Структура проекту

```text
.
├── main.py
├── privat_bank_currency_rates.py
├── index.html
├── styles/
├── Dockerfile_py
├── Dockerfile_html
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Використані технології

* Python 3.10
* asyncio
* aiohttp
* httpx
* websockets
* aiofile
* aiopath
* HTML, CSS, JavaScript
* Docker
* Docker Compose
* Nginx
* Poetry

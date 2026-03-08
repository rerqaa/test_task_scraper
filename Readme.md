# Website Scraper API

FastAPI-сервис для скрапинга веб-страниц, подсчёта вхождений заданного слова и хранения результатов в MongoDB.

## Стек

- **Python 3.10+**
- **FastAPI** — веб-фреймворк
- **Uvicorn** — ASGI-сервер
- **Motor** — асинхронный драйвер MongoDB
- **httpx** — асинхронный HTTP-клиент
- **BeautifulSoup4** — парсинг HTML

## Требования

- Python 3.10 или выше
- Запущенный экземпляр MongoDB (по умолчанию `mongodb://localhost:27017`)

## Установка

### 1. Клонирование репозитория

```bash
git clone <URL_репозитория>
cd Test_task
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
```

Активация:

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (cmd):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка среды

Сервис использует переменную окружения `MONGO_URL` для подключения к MongoDB.

- **По умолчанию:** `mongodb://localhost:27017`
- **Переопределение (PowerShell):**
  ```powershell
  $env:MONGO_URL = "mongodb://your_host:27017"
  ```
- **Переопределение (Linux / macOS):**
  ```bash
  export MONGO_URL="mongodb://your_host:27017"
  ```

## Запуск сервера

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`.

## Swagger UI

FastAPI автоматически генерирует интерактивную документацию. После запуска сервера откройте в браузере:

| Интерфейс  | URL                                      |
|------------|------------------------------------------|
| Swagger UI | `http://127.0.0.1:8000/docs`             |
| ReDoc      | `http://127.0.0.1:8000/redoc`            |

### Использование Swagger UI

1. Перейти по адресу `http://127.0.0.1:8000/docs`.
2. Выбрать нужный эндпоинт и нажать **Try it out**.
3. Заполнить параметры запроса и нажать **Execute**.
4. Результат отобразится в секции **Responses**.

## API-эндпоинты

### `POST /scan`

Сканирует указанную страницу и считает количество вхождений слова.

**Тело запроса:**
```json
{
  "url": "https://example.com",
  "word": "example"
}
```

### `GET /scans`

Возвращает список всех сканирований. Поддерживает фильтрацию через query-параметры `url` и `word`.

```
GET /scans?url=https://example.com
GET /scans?word=example
```

### `GET /scans/{id}`

Возвращает результат конкретного сканирования по его `id`.

### `POST /scans/{id}/rescan`

Повторно сканирует страницу из существующей записи и обновляет счётчик.

### `PATCH /scans/{id}`

Частично обновляет запись сканирования. Принимает любое подмножество полей `url`, `word`, `count`.

**Тело запроса (пример):**
```json
{
  "word": "new_word"
}
```

# LibraryAPI

## RESTful сервис управления библиотекой: хранение книг, авторов, учет выдачи книг, управление пользователями, JWT-аутентификация.

## 📣 Запуск с Docker Compose

Проект поддерживает запуск в контейнерах с использованием **Docker Compose**, включая:

* Django-приложение
* PostgreSQL
* Redis
* Celery (воркер)
* Celery Beat (планировщик задач)

---

### 📦 Шаги для запуска проекта в Docker

1. Убедитесь, что у вас установлены Docker и Docker Compose.

   * [Установка Docker](https://docs.docker.com/get-docker/)
   * [Установка Docker Compose](https://docs.docker.com/compose/install/)

2. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Jerikho7/LibraryAPI.git
   cd LibraryAPI
   ```

3. Создайте файл `.env`:

   ```bash
   cp .env.example .env
   ```

   Затем отредактируйте `.env`, указав переменные окружения (настройки БД, секретный ключ, параметры Redis и др.).

4. Запустите проект:

   ```bash
   docker-compose up --build
   ```

   Эта команда создаст и запустит все контейнеры, описанные в `docker-compose.yaml`.

---

### 🔎 Проверка работоспособности сервисов

| Сервис      | Проверка                                            |
| ----------- | --------------------------------------------------- |
| Django      | [http://localhost:8000](http://localhost:8000)      |
| PostgreSQL  | `docker-compose exec db psql -U $POSTGRES_USER`     |
| Redis       | `docker-compose exec redis redis-cli ping` → `PONG` |
| Celery      | `docker-compose logs -f celery`                     |
| Celery Beat | `docker-compose logs -f celery_beat`                |

---

### 🧠 Celery и Celery Beat

Celery запускается через модуль `config`, который содержит точку входа `celery.py`.

Файл `config/celery.py` должен выглядеть так:

```python
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

В `config/__init__.py` обязательно подключается приложение Celery:

```python
from .celery import app as celery_app
__all__ = ("celery_app",)
```

Команды запуска в `docker-compose.yaml`:

```yaml
celery:
  command: celery -A config worker --loglevel=info

celery_beat:
  command: celery -A config beat --loglevel=info
```

---

### ⏹️ Остановка проекта

```bash
docker-compose down
```

Чтобы также удалить tom'ы (например, с базой данных):

```bash
docker-compose down -v
```

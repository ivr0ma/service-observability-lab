# Service Observability Lab

Django-приложение для поиска похожих фильмов с полным стеком наблюдаемости: кастомные метрики Prometheus, Grafana, Node Exporter и нагрузочное тестирование через Yandex Cloud Load Testing.

## Архитектура

```
Клиент → nginx (80) → gunicorn (3 workers) → Django
                                           ↓
                                     Celery Worker
                                     Redis | Postgres

Node Exporter (9100) ─┐
Django /metrics/ (80) ─┤→ Prometheus → Grafana
```

**Машина с приложением:** nginx, Django (gunicorn 3 воркера), Celery, Redis, Postgres, Node Exporter
**Машина мониторинга:** Prometheus, Grafana

---

## Запуск приложения (App VM)

Требования: Linux/macOS, Docker.

### 1. Настройка

В [docker-compose.yml](docker-compose.yml) замените IP в `ALLOWED_HOSTS` на IP вашей App VM:

```yaml
- ALLOWED_HOSTS=localhost,<APP_VM_IP>
```

### 2. Сборка и запуск

```bash
docker compose up -d
```

Сервис поднимет: nginx, Django, Celery, Redis, Postgres, Node Exporter.

### 3. Остановка

```bash
# Остановить контейнеры
docker compose stop

# Удалить контейнеры (без томов)
docker compose down

# Удалить контейнеры и тома
docker compose down -v
```

---

## Запуск мониторинга (Monitoring VM)

### 1. Настройка Prometheus

В [monitoring/prometheus.yml](monitoring/prometheus.yml) замените IP на IP вашей App VM:

```yaml
targets:
  - "<APP_VM_IP>:9100"   # node_exporter
  - "<APP_VM_IP>:80"     # django /metrics/
```

### 2. Запуск

```bash
cd monitoring/
docker compose up -d
```

Откроется:
- Prometheus: `http://<MONITORING_VM_IP>:9090`
- Grafana: `http://<MONITORING_VM_IP>:3000` (admin / admin)

### 3. Дашборды Grafana

**Node Exporter (системные метрики):**
Импортируйте дашборд с ID `1860` через Grafana → Dashboards → Import.

**Метрики приложения:**
Импортируйте [monitoring/grafana-app-dashboard.json](monitoring/grafana-app-dashboard.json) через Grafana → Dashboards → Import → Upload JSON file.

---

## Метрики приложения

Эндпоинт: `GET /metrics/`

| Метрика | Тип | Labels | Описание |
|---|---|---|---|
| `http_requests_total` | Counter | `method`, `status_code` | Все HTTP-запросы |
| `http_post_request_duration_seconds` | Histogram | — | Latency успешных (200) POST-запросов |

Корзины гистограммы: 0.01–0.09 с шагом 0.01, затем 0.10, 0.25, 0.50, 0.75, 1.0, 2.5, 5.0, 10.0.

### PromQL для Grafana

```promql
# GET-запросы в минуту по коду ответа
rate(http_requests_total{method="get"}[1m]) * 60

# POST-запросы в минуту по коду ответа
rate(http_requests_total{method="post"}[1m]) * 60

# POST p99
histogram_quantile(0.99, rate(http_post_request_duration_seconds_bucket[5m]))

# POST p95
histogram_quantile(0.95, rate(http_post_request_duration_seconds_bucket[5m]))

# POST p90
histogram_quantile(0.90, rate(http_post_request_duration_seconds_bucket[5m]))

# POST p50
histogram_quantile(0.50, rate(http_post_request_duration_seconds_bucket[5m]))

# POST среднее
rate(http_post_request_duration_seconds_sum[5m]) / rate(http_post_request_duration_seconds_count[5m])
```

---

## Нагрузочное тестирование (Yandex Cloud Load Testing)

Конфиги и патроны: [load-testing/](load-testing/)

### GET-запросы

Конфиг: [load-testing/get-config.yaml](load-testing/get-config.yaml)

Профиль: `line` 1→50 RPS за 3 мин, затем `const` 50 RPS 1 мин.
Патроны вшиты в конфиг (URIs), отдельный файл не нужен.

**Загрузка в UI:**
1. "Файл конфигурации" → `get-config.yaml`

### POST-запросы

Конфиг: [load-testing/post-config.yaml](load-testing/post-config.yaml)
Патроны: [load-testing/post-ammo.txt](load-testing/post-ammo.txt) (генерируется скриптом ниже)

Профиль: `step` 1→10 RPS, шаг 1 RPS каждые 30 с.

**Генерация патронов:**

```bash
cd load-testing/
python gen-post-ammo.py > post-ammo.txt
```

**Загрузка в UI:**
1. "Файл конфигурации" → `post-config.yaml`
2. "Прикреплённые файлы" → `post-ammo.txt`

> Перед запуском POST-теста убедитесь, что модель обучена: `GET /train/`

### Постоянная нагрузка для мониторинга

Используйте `const`-профиль с RPS чуть ниже максимального, длительностью 1–2 часа — так графики в Grafana будут заполнены данными.

---

## Функционал сервиса

| Эндпоинт | Описание |
|---|---|
| `GET /` | Главная. Форма поиска (если модель обучена) или кнопка «Train» |
| `GET /train/` | Запустить обучение модели |
| `GET /similar/?url=<wiki_url>&cnt=<N>` | Найти N похожих фильмов по статье Wikipedia |
| `GET /metrics/` | Метрики в формате Prometheus |

### Сценарий использования

1. Открыть `http://localhost/`
2. Нажать «Train» и подождать окончания обучения
3. Ввести ссылку на английскую статью Wikipedia о фильме и число похожих
4. Получить список похожих фильмов с описаниями

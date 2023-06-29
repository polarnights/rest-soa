# Разработка REST веб-сервиса

---

<h1 align="center">Практика 4</h1>

Инструкция по запуску.

---

### 0. Установка зависимостей

```
sudo make install
sudo make requirements
python3 setup.py install
```

Для Mac с чипом M1/M2:

Слишком много проблем, нужна виртуалка.

---

### 1. Запускаем сервер

``` 
RUN_ARGS="--host localhost --port 5672 --queue rabbitmqqueue" make worker
```

---

### 2. Запускаем клиента(ов)

``` 
RUN_ARGS="--host 0.0.0.0 --port 8000 --rabbitmq_host localhost --rabbitmq_port 5672 --rabbitmq_queue rabbitmqqueue" make server
```

—

### 3. Тестируем

```
0.0.0.0:8000/docs
```

```
curl -X 'GET' \
  'http://0.0.0.0:8000/users/characters/{username}' \
  -H 'accept: application/pdf' --output profile.pdf
```

Или же с Docker:

```
docker run --rm -it -p 15672:15672 -p 8000:8000 -f Dockerfile
```

RabbitMQ мониторинг:

```
http://localhost:15672/
```

Данные для входа: username/username (log/pass)

---

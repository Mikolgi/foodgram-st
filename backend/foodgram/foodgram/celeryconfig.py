import os


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

if RABBITMQ_USER and RABBITMQ_PASSWORD:
    broker_url = (
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}"
        f"@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
    )
else:
    broker_url = f"amqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}//"

result_backend = os.getenv("CELERY_RESULT_BACKEND", "rpc://")
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"
task_default_queue = os.getenv("CELERY_DEFAULT_QUEUE", "celery")
task_routes = {
    "api.tasks.fetch_holidays": {"queue": "holidays"},
    "api.tasks.fetch_weather": {"queue": "weather"},
}

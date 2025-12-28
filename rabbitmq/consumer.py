#!/usr/bin/env python3
"""Consumer для получения сообщений из RabbitMQ"""
import sys
import functools
from vault_helper import VaultHelper
from broker_connection import RabbitMqConnection
from initializer import RabbitMQInitializer
from consumers import HolidaysConsumer, WeatherConsumer


def on_connection_ready(connection, queue_name, vault_helper):
    """Callback вызываемый когда подключение готово"""
    exchange = 'api_tasks_exchange'
    
    # Инициализируем exchange и очередь
    initializer = RabbitMQInitializer(connection, queues=[queue_name], exchange=exchange)
    initializer.init()
    
    # Определяем какой consumer использовать на основе имени очереди
    if queue_name == 'holidays_queue' or queue_name == 'holidays':
        consumer = HolidaysConsumer(connection, queue_name, vault_helper, 'holidays')
    elif queue_name == 'weather_queue' or queue_name == 'weather':
        consumer = WeatherConsumer(connection, queue_name, vault_helper, 'weather')
    else:
        print(f"Unknown queue: {queue_name}")
        print("Available queues: holidays_queue, weather_queue")
        sys.exit(1)
    
    # Запускаем consumer
    consumer.start_consuming()
    
    # IOLoop уже запущен в connection.run(), ничего дополнительного не нужно


def main():
    if len(sys.argv) < 2:
        print("Usage: python consumer.py <queue_name>")
        print("Example: python consumer.py holidays_queue")
        print("Example: python consumer.py weather_queue")
        sys.exit(1)
    
    queue_name = sys.argv[1]
    
    # Получаем учетные данные из Vault
    vault_helper = VaultHelper()
    rabbitmq_credentials = vault_helper.get_rabbitmq_credentials()
    
    # Формируем AMQP URL
    import os
    host = os.getenv('RABBITMQ_HOST', 'localhost')
    port = os.getenv('RABBITMQ_PORT', '5672')
    amqp_url = f'amqp://{rabbitmq_credentials["username"]}:{rabbitmq_credentials["password"]}@{host}:{port}/%2F'
    
    # Создаем callback
    cb = functools.partial(on_connection_ready, queue_name=queue_name, vault_helper=vault_helper)
    connection = RabbitMqConnection(amqp_url, on_ready_callback=cb)
    
    # Запускаем
    try:
        connection.run()
    except KeyboardInterrupt:
        print("\nConsumer stopped")
        connection.close()


if __name__ == '__main__':
    main()


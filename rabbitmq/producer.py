#!/usr/bin/env python3
"""Producer для отправки сообщений в RabbitMQ"""
import sys
import json
import functools
from vault_helper import VaultHelper
from broker_connection import RabbitMqConnection
from initializer import RabbitMQInitializer
from publisher import TaskPublisher


def on_connection_ready(connection, api_alias, api_params):
    """Callback вызываемый когда подключение готово"""
    exchange = 'api_tasks_exchange'
    
    # Инициализируем exchange
    initializer = RabbitMQInitializer(connection, queues=[], exchange=exchange)
    initializer.init()
    
    # Функция для закрытия соединения
    def stop_and_close():
        connection._stopping = True
        if connection._connection and connection._connection.is_open:
            connection._connection.close()
        if connection._connection:
            connection._connection.ioloop.stop()
    
    # Создаем publisher с callback для закрытия
    publisher = TaskPublisher(connection, close_callback=stop_and_close)
    
    if api_alias == 'holidays':
        publisher.publish_holidays_task(api_params)
    elif api_alias == 'weather':
        publisher.publish_weather_task(api_params)
    else:
        print(f"Unknown API alias: {api_alias}")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python producer.py <api_alias> <api_params_json>")
        print("Example: python producer.py holidays '{\"country\":\"US\",\"year\":2025,\"month\":12,\"day\":25}'")
        print("Example: python producer.py weather '{\"query\":\"New York\"}'")
        sys.exit(1)
    
    api_alias = sys.argv[1]
    api_params_str = sys.argv[2]
    
    try:
        api_params = json.loads(api_params_str)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in api_params: {e}")
        sys.exit(1)
    
    # Получаем учетные данные из Vault
    vault_helper = VaultHelper()
    rabbitmq_credentials = vault_helper.get_rabbitmq_credentials()
    
    # Формируем AMQP URL
    import os
    host = os.getenv('RABBITMQ_HOST', 'localhost')
    port = os.getenv('RABBITMQ_PORT', '5672')
    amqp_url = f'amqp://{rabbitmq_credentials["username"]}:{rabbitmq_credentials["password"]}@{host}:{port}/%2F'
    
    # Создаем callback
    cb = functools.partial(on_connection_ready, api_alias=api_alias, api_params=api_params)
    connection = RabbitMqConnection(amqp_url, on_ready_callback=cb)
    
    # Запускаем
    connection.run()


if __name__ == '__main__':
    main()


import logging
from broker_connection import RabbitMqConnection
import pika
import json

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


class TaskPublisher:
    ROUTING_KEY_FOR_HOLIDAYS = 'holidays'
    ROUTING_KEY_FOR_WEATHER = 'weather'
    EXCHANGE = 'api_tasks_exchange'
    _close_callback = None

    def __init__(self, connection: RabbitMqConnection, close_callback=None):
        self._connection = connection
        self._close_callback = close_callback
        self.__setup_delivery_confirmation()

    def __setup_delivery_confirmation(self):
        """
        Setup delivery confirmation callback.

        This method adds the delivery confirmation callback to the
        channel. When a message is confirmed or rejected by RabbitMQ,
        the __on_delivery_confirmation method will be called with a
        pika.frame.Method object as an argument. The method object
        contains information about whether the message was confirmed or
        rejected.
        """
        self._connection.channel.confirm_delivery(self.__on_delivery_confirmation)

    def __on_delivery_confirmation(self, method_frame):
        """
        Called when a message is confirmed or rejected by RabbitMQ.

        :param pika.frame.Method method_frame: The Basic.Ack or Basic.Nack frame

        This method is a callback that is added to the channel using the
        add_on_delivery_confirmation_callback method. When a message is confirmed
        or rejected by RabbitMQ, this method is called with a
        pika.frame.Method object as an argument. The method object
        contains information about whether the message was confirmed or
        rejected.
        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        if confirmation_type == 'ack':
            LOGGER.debug("Message confirmed")
            # Вызываем callback для закрытия соединения если есть
            if self._close_callback:
                self._connection._connection.ioloop.call_later(0.1, self._close_callback)
        else:
            LOGGER.warning("Message rejected")

    def publish_holidays_task(self, api_params):
        """
        Publish a holidays task.

        :param dict api_params: Parameters for holidays API (country, year, month, day)
        """
        channel = self._connection.channel
        properties = pika.BasicProperties(
            app_id='holidays-publisher',
            content_type='application/json',
            delivery_mode=2  # Make message persistent (durable)
        )

        message = {
            'api_alias': 'holidays',
            'api_params': api_params
        }

        channel.basic_publish(
            self.EXCHANGE,
            self.ROUTING_KEY_FOR_HOLIDAYS,
            json.dumps(message, ensure_ascii=False),
            properties
        )

        LOGGER.info('Published holidays task with params: %s', api_params)

    def publish_weather_task(self, api_params):
        """
        Publish a weather task.

        :param dict api_params: Parameters for weather API (query)
        """
        channel = self._connection.channel
        properties = pika.BasicProperties(
            app_id='weather-publisher',
            content_type='application/json',
            delivery_mode=2  # Make message persistent (durable)
        )

        message = {
            'api_alias': 'weather',
            'api_params': api_params
        }

        channel.basic_publish(
            self.EXCHANGE,
            self.ROUTING_KEY_FOR_WEATHER,
            json.dumps(message, ensure_ascii=False),
            properties
        )

        LOGGER.info('Published weather task with params: %s', api_params)


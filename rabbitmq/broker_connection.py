import logging
import pika

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


class RabbitMqConnection:
    def __init__(self, amqp_url, on_ready_callback):
        """
        Initialize the RabbitMqConnection object.

        :param str amqp_url: The AMQP URL used to connect to RabbitMQ
        """
        self.amqp_url = amqp_url
        self._connection = None
        self._channel = None
        self._stopping = False
        self._ready = False
        self._on_ready_callback = on_ready_callback

    def connect(self):
        """
        Establish a connection to RabbitMQ using the given AMQP URL.

        :rtype: pika.SelectConnection
        :return: The connection handle
        """
        LOGGER.info('Connecting to %s', self.amqp_url)
        return pika.SelectConnection(
            pika.URLParameters(self.amqp_url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.close)

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection
        """
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        LOGGER.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.
        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self._ready = True
        self.add_on_channel_close_callback()

        if self._on_ready_callback:
            LOGGER.info('Calling ready callback')
            self._on_ready_callback(self)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._stopping and self._connection and self._connection.is_open:
            self._stopping = True
            self._connection.close()

    @property
    def channel(self):
        if not self._ready:
            raise RuntimeError("Connection not ready")
        return self._channel

    @property
    def ready(self):
        return self._ready and self._channel and self._channel.is_open

    def close(self, _unused_connection=None, _unused_reason=None):
        """This method closes the connection to RabbitMQ."""
        if self._connection is not None and self._connection.is_open:
            LOGGER.info('Closing connection')
            self._stopping = True
            self._connection.close()

    def is_connect(self):
        """
        Check if the connection to RabbitMQ is established.

        :return: True if the connection is established, False otherwise
        """
        return self._connection and self._connection.is_open

    def run(self):
        """Запуск IOLoop"""
        self._connection = self.connect()
        self._connection.ioloop.start()


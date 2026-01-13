__all__ = (
    "broker",
    # "user_registered_pub",
)

from faststream.rabbit import RabbitBroker
from src.config import config

broker = RabbitBroker(config.rabbitmq.url)

# user_registered_pub = broker.publish("user.{user_id}.created")

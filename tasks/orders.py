#!/usr/bin/python3
"""
Module: tasks
Description: Celery tasks for web crawling and related functionalities.
"""

import celery

from log import LOGGER as log
import redis
from typing import Dict
import orjson as json
import random
import time
from config import (
    REDIS_URL,
    REDIS_URL_LOCALHOST,
    ORDER_KEY,
    TASK_ID_KEY,
    EXECUTED_ORDERS_KEY,
    ORDER_STATUS_KEY,
)
from data_types import OrderStatus

REDIS_URL = REDIS_URL_LOCALHOST  # noqa

celery_worker = celery.Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.orders"],
)


redis_pool = redis.ConnectionPool.from_url(REDIS_URL)


def get_delay():
    return random.randint(3, 10)


@celery_worker.task(
    name="store_executed_order",
    bind=True,
)
def store_executed_order(self, order_id: str, order_data: Dict):
    """
    Accepts order id and data, stores it and returns response.

    Returns:
    - dict: Dictionary containing response
    """
    log.info(f"Storing order: {order_id}")
    with redis.Redis(connection_pool=redis_pool) as redis_client:
        redis_client.lpush(EXECUTED_ORDERS_KEY.format("ABCD"), json.dumps(order_data))
    return {"status": "Done"}


@celery_worker.task(
    name="execute_limit_order",
    bind=True,
)
def execute_limit_order(self, order_id: str, delay: int = 1):
    """
    Accepts order id, executes it and returns response.

    Returns:
    - dict: Dictionary containing response
    """

    log.info(f"Executing order: {order_id}")
    with redis.Redis(connection_pool=redis_pool) as redis_client:
        order = redis_client.get(ORDER_KEY.format(order_id))
        if order:
            order_data = json.loads(order)
            log.info(f"Order data: {order_data}")
            time.sleep(delay)
            redis_client.set(
                ORDER_STATUS_KEY.format(order_id), OrderStatus.FILLED.value
            )
            _ = store_executed_order.delay(order_id, order_data)
            return {"status": "Done"}
    return {"status": "Invalid Order"}


@celery_worker.task(
    name="send_limit_order",
    bind=True,
)
def send_limit_order(self, limit_order_data: Dict):
    """
    Accepts limit order, adds it to queue and returns response.

    Returns:
    - dict: Dictionary containing response
    """
    log.info(f"Sending limit order: {limit_order_data}")
    with redis.Redis(connection_pool=redis_pool) as redis_client:
        redis_client.set(
            ORDER_KEY.format(limit_order_data.get("order_id")),
            json.dumps(limit_order_data),
        )
        redis_client.set(
            ORDER_STATUS_KEY.format(limit_order_data.get("order_id")),
            OrderStatus.PENDING.value,
        )
    delay = get_delay()
    result = execute_limit_order.delay(limit_order_data.get("order_id"), delay)
    task_id = result.id
    with redis.Redis(connection_pool=redis_pool) as redis_client:
        redis_client.set(
            TASK_ID_KEY.format(limit_order_data.get("order_id")), str(task_id)
        )
    return {"status": "Done"}


celery_worker.conf.task_routes = {
    "tasks.orders.send_limit_order": "tasks",
    "tasks.orders.execute_limit_order": "tasks",
}

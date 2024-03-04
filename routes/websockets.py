from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import orjson as json
from typing import Optional
from utils import (PriceCalculator, ExchangeLimitOrderCalculator,
                   measure_latency)
from data_types import Operation
from models import LimitOrder

# from log import LOGGER as log
from redis import asyncio as aioredis
from tasks.orders import send_limit_order, celery_worker
from log import LOGGER as log
from uuid import uuid4
from config import (REDIS_URL_LOCALHOST, TASK_ID_KEY, EXECUTED_ORDERS_KEY,
                    WS_PREFIX, ORDER_BOOK_ENDPOINT, LIMIT_ORDER_ENDPOINT,
                    EXECUTE_LIMIT_ORDER_ENDPOINT,
                    GET_LIMIT_ORDER_STATUS_ENDPOINT,
                    GET_EXECUTED_ORDERS_ENDPOINT)
from celery.result import AsyncResult
from pydantic import ValidationError


ws_router = APIRouter(prefix=WS_PREFIX)


async def get_order_book_prices(
    websocket: WebSocket, currency_pair: str, quantity: float
) -> tuple[float, float]:
    order_books = websocket.app.get_app_order_book(currency_pair)
    if order_books is None:
        log.error("Order book not found")
        raise ValueError("Order book not found")
    buy_price = PriceCalculator.calculate_price(order_books, Operation.BUY,
                                                quantity)
    sell_price = PriceCalculator.calculate_price(order_books, Operation.SELL,
                                                 quantity)
    return buy_price * quantity, sell_price * quantity


async def receive_json(websocket: WebSocket) -> Optional[dict]:
    try:
        data = await websocket.receive_text()
        return json.loads(data)
    except json.JSONDecodeError as e:
        log.error(f"JSON decoding error: {e}")
        return None
    except WebSocketDisconnect:
        return None


async def handle_websocket(websocket: WebSocket, handler):
    await websocket.accept()
    try:
        while True:
            json_data = await receive_json(websocket)
            if json_data is None:
                break
            await handler(websocket, json_data)
    except Exception as e:
        log.error(f"An error occurred: {e}")
        await websocket.send_text(f"Error: {e}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass


@ws_router.websocket(ORDER_BOOK_ENDPOINT)
@measure_latency
async def order_book_websocket_endpoint(websocket: WebSocket):
    async def handler(websocket: WebSocket, json_data):
        try:
            currency_pair = json_data["currencyPair"]
            quantity = float(json_data["quantity"])
            buy_price, sell_price = await get_order_book_prices(
                websocket, currency_pair, quantity
            )
            data = {"buy_price": buy_price, "sell_price": sell_price}
            await websocket.send_json(data)
        except (ValueError, Exception) as e:
            log.error(f"Error: {e}")
            await websocket.send_text(f"Error: {e}")

    await handle_websocket(websocket, handler)


@ws_router.websocket(LIMIT_ORDER_ENDPOINT)
@measure_latency
async def limit_order_websocket_endpoint(websocket: WebSocket):
    async def handler(websocket: WebSocket, json_data):
        try:
            currency_pair = json_data["currencyPair"]
            quantity = float(json_data["quantity"])
            operation = json_data["operation"]
            order_books = websocket.app.get_app_order_book(currency_pair)
            if order_books:
                limit_orders = (
                    ExchangeLimitOrderCalculator.get_best_limit_orders(  # noqa
                        order_books, operation, quantity
                    )
                )
            data = {
                "limit_orders": json.loads(json.dumps(limit_orders))
                if limit_orders
                else []
            }
            await websocket.send_json(data)
        except (ValueError, Exception) as e:
            log.error(f"Error: {e}")
            await websocket.send_text(f"Error: {e}")

    await handle_websocket(websocket, handler)


@ws_router.websocket(EXECUTE_LIMIT_ORDER_ENDPOINT)
@measure_latency
async def execute_limit_order_websocket_endpoint(websocket: WebSocket):
    async def handler(websocket: WebSocket, json_data):
        try:
            order_id = uuid4().hex
            json_data["order_id"] = order_id
            LimitOrder(**json_data)  # Validate limit order
            send_limit_order.delay(json_data)
            response = {"status": "SUCCESS", "order_id": order_id}
            await websocket.send_json(response)
        except (ValueError, ValidationError, Exception) as ve:
            log.error(f"Error: {ve}")
            resp = {"status": "FAILED", "error": str(ve)}
            await websocket.send_json(resp)

    await handle_websocket(websocket, handler)


@ws_router.websocket(GET_LIMIT_ORDER_STATUS_ENDPOINT)
@measure_latency
async def get_limit_order_websocket_endpoint(websocket: WebSocket):
    async def handler(websocket: WebSocket, json_data):
        try:
            order_id = json_data["orderId"]
            async with aioredis.from_url(REDIS_URL_LOCALHOST) as redis_client:
                task_id = await redis_client.get(TASK_ID_KEY.format(order_id))
            result = AsyncResult(id=task_id, app=celery_worker)
            data = {
                "status": result.status,
                "result": result.result if result.result else "",
                "orderId": order_id,
            }
            await websocket.send_json(data)
        except (ValueError, Exception) as e:
            log.error(f"Error: {e}")
            resp = {"status": "FAILED", "error": str(e)}
            await websocket.send_json(resp)

    await handle_websocket(websocket, handler)


@ws_router.websocket(GET_EXECUTED_ORDERS_ENDPOINT)
@measure_latency
async def get_executed_orders(websocket: WebSocket):
    async def handler(websocket: WebSocket, json_data):
        try:
            client_id = json_data["clientId"]
            client_id = "ABCD"
            async with aioredis.from_url(REDIS_URL_LOCALHOST) as redis_client:
                orders = await redis_client.lrange(
                    EXECUTED_ORDERS_KEY.format(client_id), 0, -1
                )
            data = {"executed_orders": orders}
            await websocket.send_json(data)
        except (ValueError, Exception) as e:
            log.error(f"Error: {e}")
            resp = {"status": "FAILED", "error": str(e)}
            await websocket.send_json(resp)

    await handle_websocket(websocket, handler)

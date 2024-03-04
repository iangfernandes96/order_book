#!/usr/bin/python3
# pylint: disable=E0401

"""
    Module: main
    Description: FastAPI application configuration and startup logic.
"""
import asyncio
from itertools import permutations
from typing import Tuple, List
from fastapi import FastAPI
from fastapi_lifespan_manager import LifespanManager
from fastapi.middleware.cors import CORSMiddleware
from routes.websockets import ws_router
from main import fetch_all_order_books
from utils import OrderBookMerger
from data_types import OrderData


manager = LifespanManager()


class OrderBookFastAPI(FastAPI):
    def initialize_app_order_book(self):
        if not app.extra.get("order_book"):
            app.extra["order_book"] = {}

    def get_app_order_book(self, pair: str):
        return app.extra.get("order_book", {}).get(pair)

    def set_app_order_book(
        self, pair: str, order_books: Tuple[List[OrderData], List[OrderData]]
    ):
        app.extra["order_book"][pair] = order_books

    def flush_app_order_book(self):
        if app.extra.get("order_book"):
            app.extra["order_book"] = {}


async def update_order_book(web_app: OrderBookFastAPI, pair: str, interval: float):
    while True:
        await asyncio.sleep(interval)
        order_books = await fetch_all_order_books(pair)
        if order_books is not None:
            merged_order_book = OrderBookMerger.merge_order_books(order_books)
            web_app.set_app_order_book(pair, merged_order_book)


@manager.add  # type: ignore
async def start_up(web_app: OrderBookFastAPI):
    web_app.initialize_app_order_book()
    pairs = ["BTCUSD", "ETHUSD"]
    intervals = [1.2, 2.3, 3.4]
    permut = permutations(intervals, len(pairs))
    unique_comb = []
    for comb in permut:
        zipped = zip(comb, pairs)
        unique_comb.extend(list(zipped))
    for interval, pair in unique_comb:
        asyncio.create_task(update_order_book(app, pair, interval))
    yield
    web_app.flush_app_order_book()


app = OrderBookFastAPI(lifespan=manager)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(router, prefix="/api")
app.include_router(ws_router)

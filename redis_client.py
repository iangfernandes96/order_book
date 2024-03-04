# from typing import List, Tuple
# from order_books import OrderData
# from redis import asyncio as aioredis
# import orjson as json
# from utils import OrderBookMerger


# class RedisOrderBookStorage:
#     def __init__(self) -> None:
#         self.redis_url = "redis://localhost:6379"

#     @staticmethod
#     def get_serialized_order_book(order_book: List[OrderData]) -> bytes:
#         serialized_order_book = [order.__dict__ for order in order_book]
#         return json.dumps(serialized_order_book)

#     @staticmethod
#     def get_deserialized_order_book(order_book_bytes:
#                                     bytes) -> List[OrderData]:
#         deserialized_order_book = json.loads(order_book_bytes)
#         return [OrderData.from_order(data)
#                 for data in deserialized_order_book]

#     async def store_order_book(self, pair: str,
#                                order_books: Tuple[List[OrderData],
#                                                   List[OrderData]]):
#         """
#         Store the order book data in Redis asynchronously.

#         Args:
#             pair (str): The currency pair identifier.
#             bids (List[OrderData]): List of bid orders.
#             asks (List[OrderData]): List of ask orders.
#         """
#         bids, asks = order_books
#         async with aioredis.from_url(self.redis_url) as redis_client:
#             # Store bid orders in a Sorted Set with price as score
#             await redis_client.set(f"{pair}:bids",
#                                    self.get_serialized_order_book(bids))
#             await redis_client.set(f"{pair}:asks",
#                                    self.get_serialized_order_book(asks))

#     async def update_order_book(self, pair: str,
#                                 order_books: Tuple[List[OrderData],
#                                                    List[OrderData]]):
#         """
#         Update the order book data in Redis asynchronously.

#         Args:
#             pair (str): The currency pair identifier.
#             bids (List[OrderData]): List of bid orders to update.
#             asks (List[OrderData]): List of ask orders to update.
#         """
#         existing_order_book = await self.get_order_book(pair)
#         if existing_order_book:
#             merged_order_books = OrderBookMerger.merge_order_books(
#              [existing_order_book, order_books])
#             await self.store_order_book(pair, merged_order_books)
#         else:
#             await self.store_order_book(pair, order_books)

#     async def get_order_book(self, pair: str) -> Tuple[List[OrderData],
#                                                        List[OrderData]]:
#         """
#         Retrieve the order book data from Redis asynchronously.

#         Args:
#             pair (str): The currency pair identifier.

#         Returns:
#             Tuple[List[OrderData], List[OrderData]]: A tuple containing bid
#             and ask orders.
#         """
#         async with aioredis.from_url(self.redis_url) as redis_client:
#             # Retrieve bid and ask orders from Sorted Sets
#             bids_bytes = await redis_client.get(f"{pair}:bids")
#             asks_bytes = await redis_client.get(f"{pair}:asks")
#             if bids_bytes and asks_bytes:
#                 bids = self.get_deserialized_order_book(bids_bytes)
#                 asks = self.get_deserialized_order_book(asks_bytes)
#                 return bids, asks
#             return [], []

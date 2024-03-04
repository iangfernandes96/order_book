# class AsyncDict:
#     def __init__(self, loop=None):
#         self.loop = loop or asyncio.get_event_loop()
#         self.data = {}

#     def set(self, key, value):
#         self.data[key] = value

#     def get(self, key):
#         return self.data.get(key)

#     def delete(self, key):
#         del self.data[key]


# class OrderBookStorage(AsyncDict):
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             print("Initialized order book")
#             cls._instance = super(OrderBookStorage, cls).__new__(cls)
#             cls._instance.data = {}
#         else:
#             print(f"""Found existing instance,
#                   with data: {cls._instance.data.keys()}""")
#         return cls._instance

#     def store_order_book(self, pair, order_books):
#         if not self.data.get(pair):
#             self.set(pair, order_books)
#         else:
#             self.update_existing_order_book(pair, order_books)

#     def update_existing_order_book(self, pair, order_books):
#         if not self.data.get(pair):
#             self.set(pair, order_books)
#             return
#         else:
#             # Do not use
#             self.set(pair, OrderBookMerger.merge_order_books(
#                 [order_books, order_books]))

#     def get_order_book(self, pair):
#         return self.get(pair)

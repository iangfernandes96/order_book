import asyncio
from functools import wraps

from typing import List, Tuple
from collections import defaultdict
from order_books import OrderData
from data_types import Operation


class OrderBookMerger:
    """Utility class for merging order books from multiple exchanges."""

    @staticmethod
    def merge_order_books(
        order_books: List[Tuple[List[OrderData], List[OrderData]]]
    ) -> Tuple[List[OrderData], List[OrderData]]:
        """
        Merge order books from multiple exchanges.

        Args:
            order_books (List[Tuple[List[OrderData], List[OrderData]]]):
                List of tuples containing bid and ask order books from each
                exchange.

        Returns:
            Tuple[List[OrderData], List[OrderData]]: Merged bid and ask order
            books.
        """
        bids = []
        asks = []
        for exchange_bids, exchange_asks in order_books:
            bids.extend(exchange_bids)
            asks.extend(exchange_asks)
        return sorted(bids, key=lambda x: x.price, reverse=True), sorted(
            asks, key=lambda x: x.price
        )


class PriceCalculator:
    """Utility class for calculating the price based on merged order books."""

    @staticmethod
    def calculate_price(
        order_books: Tuple[List[OrderData], List[OrderData]],
        operation: Operation,
        quantity: float,
    ) -> float:
        """
        Calculate the price based on merged order books.

        Args:
            order_books (Tuple[List[OrderData], List[OrderData]]):
                Tuple containing merged bid and ask order books.
            operation (Operation): The type of operation, either BUY or SELL.
            quantity (float): The quantity of cryptocurrency for which to
            calculate the price.

        Returns:
            float: The calculated price.
        """
        bids, asks = order_books
        total_quantity, total_cost = 0.0, 0.0
        orders = asks if operation == Operation.BUY else bids
        for order in orders:
            if total_quantity + order.amount <= quantity:
                total_quantity += order.amount
                total_cost += order.amount * order.price
            else:
                remaining_quantity = quantity - total_quantity
                total_quantity += remaining_quantity
                total_cost += remaining_quantity * order.price
                break  # Stop iterating since required quantity is reached

        return total_cost / total_quantity if total_quantity > 0.0 else 0.0


class ExchangeLimitOrderCalculator:
    @staticmethod
    def get_best_limit_orders(
        order_books: Tuple[List[OrderData], List[OrderData]],
        operation: Operation,
        quantity: float,
    ) -> List[OrderData]:
        bids, asks = order_books
        total_quantity, total_cost = 0.0, 0.0
        temp_dict = defaultdict(defaultdict)
        orders = asks if operation == Operation.BUY else bids
        for order in orders:
            if total_quantity + order.amount <= quantity:
                total_quantity += order.amount
                total_cost += order.amount * order.price
                if not temp_dict[order.exchange].get("quantity"):
                    temp_dict[order.exchange]["quantity"] = order.amount
                else:
                    temp_dict[order.exchange]["quantity"] += order.amount
                temp_dict[order.exchange]["price"] = order.price
            else:
                remaining_quantity = quantity - total_quantity
                total_quantity += remaining_quantity
                total_cost += remaining_quantity * order.price
                if not temp_dict[order.exchange].get("quantity"):
                    temp_dict[order.exchange]["quantity"] = remaining_quantity
                else:
                    temp_dict[order.exchange]["quantity"] += remaining_quantity
                temp_dict[order.exchange]["price"] = order.price
                break
        return [
            OrderData(
                price=data["price"],
                amount=data["quantity"],
                timestamp=0,
                exchange=exchange,
            )
            for exchange, data in temp_dict.items()
        ]


def measure_latency(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        result = await func(*args, **kwargs)
        end_time = asyncio.get_event_loop().time()
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")
        return result

    return wrapper

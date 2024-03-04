import time

from typing import List
import asyncio
import argparse
from asyncio import TimeoutError
from aiohttp import ClientError
from order_books import (
    CoinbaseOrderBook,
    GeminiOrderBook,
    KrakenOrderBook,
    ExchangeOrderBook,
)
from utils import PriceCalculator, OrderBookMerger
from data_types import BTCUSDExchangePairs, Operation, ETHUSDExchangePairs
from log import LOGGER as log


def get_exchange_pair_order_book(pair: str) -> List[ExchangeOrderBook]:
    exchange_pairs = {
        "BTCUSD": [
            CoinbaseOrderBook(BTCUSDExchangePairs.COINBASE),
            KrakenOrderBook(BTCUSDExchangePairs.KRAKEN),
            GeminiOrderBook(BTCUSDExchangePairs.GEMINI),
        ],
        "ETHUSD": [
            CoinbaseOrderBook(ETHUSDExchangePairs.COINBASE),
            KrakenOrderBook(ETHUSDExchangePairs.KRAKEN),
            GeminiOrderBook(ETHUSDExchangePairs.GEMINI),
        ],
    }

    if pair in exchange_pairs:
        return exchange_pairs[pair]
    raise ValueError("Invalid pair")


async def fetch_all_order_books(pair: str):
    """
    Fetch standardized order books for a currency pair
    from multiple exchanges asynchronously.

    Returns:
        Union[Tuple[List[OrderData], List[OrderData]], None]: A tuple
        containing standardized bids and asks from multiple exchanges,
        or None if an error occurs.
    """
    exchange_order_books = get_exchange_pair_order_book(pair)
    tasks = [
        exchange_order_book.get_standardized_order_book()
        for exchange_order_book in exchange_order_books
    ]
    try:
        return await asyncio.gather(*tasks)
    except ClientError as ce:
        log.exception(f"Aiohttp Client Error occurred: {ce}")
    except TimeoutError as te:
        log.exception(f"Asyncio Request timed out: {te}")
    except Exception as e:
        log.exception(f"An unexpected error occurred: {e}")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantity", type=float, default=10.0)
    args = parser.parse_args()
    quantity = args.quantity

    try:
        order_books = asyncio.run(fetch_all_order_books("BTCUSD"))
        if order_books is not None:
            merged_order_book = OrderBookMerger.merge_order_books(order_books)

            buy_price = PriceCalculator.calculate_price(
                merged_order_book, Operation.BUY, quantity
            )

            sell_price = PriceCalculator.calculate_price(
                merged_order_book, Operation.SELL, quantity
            )

            print(f"To BUY {quantity} BTC: ${buy_price * quantity:.4f}")
            print(f"To SELL {quantity} BTC: ${sell_price * quantity:.4f}")
        else:
            raise Exception("Error fetching order books from exchange")
    except Exception as e:
        log.exception(f"An error occurred: {e}")
        print("An error occurred, please check app.log for more details")


if __name__ == "__main__":
    start_time = time.monotonic()
    main()
    execution_time = time.monotonic() - start_time
    print(f"Execution time: {execution_time:.4f} seconds")

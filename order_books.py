from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
from aiohttp import ClientSession
from data_types import OrderData, ExchangePairs


class ExchangeOrderBook(ABC):
    """
    Abstract base class for exchange-specific order book implementations.

    Attributes:
        pair (BTCUSDExchangePairs): The cryptocurrency pair for the order book.
        _url (str): The exchange-specific API endpoint URL.
    """

    __slots__ = (
        "pair",
        "_url",
    )

    def __init__(self, pair: ExchangePairs) -> None:
        self.pair = pair
        self._url = self._get_exchange_url()

    @abstractmethod
    def _get_exchange_url(self):
        """Return the exchange-specific API endpoint URL."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_order_book(self):
        """Fetch raw order book data from the exchange API."""
        raise NotImplementedError

    @abstractmethod
    async def get_standardized_order_book(self):
        """Fetch and standardize order book data from the exchange API."""
        raise NotImplementedError

    @staticmethod
    async def get_order_book_from_exchange(url: str) -> Dict[str, Any]:
        """
        Make a generic request to an exchange API and return order book data.

        Args:
            url (str): The API endpoint URL.

        Returns:
            Dict[str, Any]: The raw order book data.
        """
        headers = {"Accept-Encoding": "gzip"}
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    def _standardize_order_book(
        bids: List[Any], asks: List[Any], exchange: str
    ) -> Tuple[List[OrderData], List[OrderData]]:
        """
        Standardize raw order book data.

        Args:
            bids (List[Any]): Raw bid data from the exchange.
            asks (List[Any]): Raw ask data from the exchange.

        Returns:
            Tuple[List[OrderData], List[OrderData]]: Standardized bid and ask
                                                     data.
        """
        standardized_bids = [
            OrderData.from_order(order, exchange) for order in bids
        ]  # noqa
        standardized_asks = [
            OrderData.from_order(order, exchange) for order in asks
        ]  # noqa
        return standardized_bids, standardized_asks


class CoinbaseOrderBook(ExchangeOrderBook):
    def _get_exchange_url(self) -> str:
        return f"https://api.pro.coinbase.com/products/{self.pair}/book?level=2"  # noqa

    async def fetch_order_book(self) -> Tuple[List, List]:
        order_book = await self.get_order_book_from_exchange(self._url)
        return order_book["bids"], order_book["asks"]

    async def get_standardized_order_book(
        self,
    ) -> Tuple[List[OrderData], List[OrderData]]:
        bids, asks = await self.fetch_order_book()
        return self._standardize_order_book(bids, asks, exchange="COINBASE")


class GeminiOrderBook(ExchangeOrderBook):
    def _get_exchange_url(self) -> str:
        return f"https://api.gemini.com/v1/book/{self.pair}"

    async def fetch_order_book(self) -> Tuple[List, List]:
        order_book = await self.get_order_book_from_exchange(self._url)
        return order_book["bids"], order_book["asks"]

    async def get_standardized_order_book(
        self,
    ) -> Tuple[List[OrderData], List[OrderData]]:
        bids, asks = await self.fetch_order_book()
        return self._standardize_order_book(bids, asks, exchange="GEMINI")


class KrakenOrderBook(ExchangeOrderBook):
    def _get_exchange_url(self) -> str:
        return f"https://api.kraken.com/0/public/Depth?pair={self.pair}"

    def _get_result_key(self) -> str:
        if self.pair == "XBTUSD":
            return "XXBTZUSD"
        if self.pair == "ETHUSD":
            return "XETHZUSD"
        return ""

    async def fetch_order_book(self) -> Tuple[List, List]:
        order_book = await self.get_order_book_from_exchange(self._url)
        result_key = self._get_result_key()
        order_book_result = order_book["result"].get(result_key)
        return order_book_result["bids"], order_book_result["asks"]

    async def get_standardized_order_book(
        self,
    ) -> Tuple[List[OrderData], List[OrderData]]:
        bids, asks = await self.fetch_order_book()
        return self._standardize_order_book(bids, asks, exchange="KRAKEN")

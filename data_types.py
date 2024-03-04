from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Any, overload


class ExchangePairs(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class BTCUSDExchangePairs(ExchangePairs):
    """
    Enum representing BTC to USD exchange pairs.

    Values:
        COINBASE (str): Coinbase exchange pair.
        KRAKEN (str): Kraken exchange pair.
        GEMINI (str): Gemini exchange pair.
    """

    COINBASE = "BTC-USD"
    KRAKEN = "XBTUSD"
    GEMINI = "BTCUSD"


class ETHUSDExchangePairs(ExchangePairs):
    """
    Enum representing ETH to USD exchange pairs.

    Values:
        COINBASE (str): Coinbase exchange pair.
        KRAKEN (str): Kraken exchange pair.
        GEMINI (str): Gemini exchange pair.
    """

    COINBASE = "ETH-USD"
    KRAKEN = "ETHUSD"
    GEMINI = "ETHUSD"


class OrderStatus(str, Enum):
    """
    Enum representing order statuses.

    Values:
        FILLED (str): Order is filled.
        PARTIALLY_FILLED (str): Order is partially filled.
        CANCELLED (str): Order is cancelled.
        PENDING (str): Order is pending.
    """

    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str.__str__(self)


class Operation(str, Enum):
    """
    Enum representing buy (BUY) or sell (SELL) operations.

    Values:
        BUY (str): Buy operation.
        SELL (str): Sell operation.
    """

    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        return str.__str__(self)


@dataclass(frozen=True)
class OrderData:
    """
    Dataclass representing order data.

    Attributes:
        price (float): The price of the order.
        amount (float): The amount of cryptocurrency in the order.
        timestamp (int): The timestamp of the order.
        exchange (str): The exchange where the order is placed.

    Class Methods:
        from_order(cls, item: Tuple) -> OrderData: Create OrderData from a
                                                   tuple.
        from_order(cls, item: dict) -> OrderData: Create OrderData from a
                                                  dictionary.
        from_order(cls, item: Any) -> OrderData: Create OrderData from a
                                                  generic item.
    """

    __slots__ = ("price", "amount", "timestamp", "exchange")
    price: float
    amount: float
    timestamp: int
    exchange: str

    @overload
    @classmethod
    def from_order(cls, item: Tuple, exchange: str) -> "OrderData":
        ...

    @overload
    @classmethod
    def from_order(cls, item: dict, exchange: str) -> "OrderData":
        ...

    @classmethod
    def from_order(cls, item: Any, exchange: str) -> "OrderData":
        """
        Create an OrderData instance from a generic item.

        Args:
            item (Any): The item representing order data, either a tuple or a
                        dictionary.

        Returns:
            OrderData: An instance of OrderData.

        Raises:
            TypeError: If the type of 'item' is not supported.
        """
        if isinstance(item, list):
            price = float(item[0])
            amount = float(item[1])
            timestamp = int(item[2])
        elif isinstance(item, dict):
            price = float(item["price"])
            amount = float(item["amount"])
            timestamp = int(item["timestamp"])
        else:
            raise TypeError(f"Unsupported type for 'item': {type(item)}")
        return cls(price, amount, timestamp, exchange)

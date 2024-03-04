from typing import Optional
from pydantic import BaseModel, Field
from data_types import Operation


class LimitOrder(BaseModel):
    order_id: str
    price: float
    amount: float
    timestamp: Optional[int]
    exchange: str
    operation: Operation
    currency_pair: str


class GetLimitOrdersRequest(BaseModel):
    currency_pair: str = Field(alias="currencyPair")
    quantity: float
    operation: Operation

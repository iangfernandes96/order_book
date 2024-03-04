from utils import PriceCalculator
from data_types import Operation
from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/price")
async def get_price(request: Request):
    buy_price = PriceCalculator.calculate_price(
        request.app.get_app_order_book("BTC-USD"), Operation.BUY, 10
    )

    sell_price = PriceCalculator.calculate_price(
        request.app.get_app_order_book("BTC-USD"), Operation.SELL, 10
    )
    return {
        "buy_price": f"{buy_price * 10:.4f}",
        "sell_price": f"{sell_price * 10:.4f}",
    }

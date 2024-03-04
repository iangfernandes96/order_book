REDIS_URL = "redis://redis:6379/0"

REDIS_URL_LOCALHOST = "redis://localhost:6379/0"

# Websocket endpoints
WS_PREFIX = "/ws"
ORDER_BOOK_ENDPOINT = "/order-book"
LIMIT_ORDER_ENDPOINT = "/limit-order"
EXECUTE_LIMIT_ORDER_ENDPOINT = "/execute-limit-order"
GET_LIMIT_ORDER_STATUS_ENDPOINT = "/get-limit-order-status"
GET_EXECUTED_ORDERS_ENDPOINT = "/get-executed-orders"


# Redis Keys
ORDER_KEY = "order:{}"
TASK_ID_KEY = "order:{}:task_id"
EXECUTED_ORDERS_KEY = "executed_orders:{}"
ORDER_STATUS_KEY = "order:{}:status"

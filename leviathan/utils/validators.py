"""Input validation utilities."""
import re


def validate_symbol(symbol: str) -> bool:
    return bool(re.match(r'^[A-Z]{1,5}(/[A-Z]{1,5})?$', symbol.upper()))


def validate_quantity(qty: float) -> bool:
    return qty > 0


def validate_price(price: float) -> bool:
    return price > 0


def validate_order_params(symbol: str, qty: float, side: str,
                           order_type: str = 'market') -> tuple[bool, str]:
    if not validate_symbol(symbol):
        return False, f"Invalid symbol: {symbol}"
    if not validate_quantity(qty):
        return False, f"Invalid quantity: {qty}"
    if side.lower() not in ('buy', 'sell'):
        return False, f"Invalid side: {side}"
    if order_type not in ('market', 'limit', 'stop', 'stop_limit'):
        return False, f"Invalid order type: {order_type}"
    return True, ""

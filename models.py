from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    balance: float = 0.0
    referral_count: int = 0
    referral_id: Optional[int] = None
    is_admin: bool = False

@dataclass
class Order:
    order_id: str
    user_id: int
    product_id: str
    amount: float
    status: str = "pending"  # pending, paid, cancelled
    payment_method: Optional[str] = None
    created_at: Optional[str] = None
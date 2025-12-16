import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict

DATA_FILE = "data/users.json"
ORDERS_FILE = "data/orders.json"


@dataclass
class User:
    user_id: int
    username: Optional[str]
    full_name: str
    balance: int = 0
    total_orders: int = 0
    registered_at: str = ""
    used_promocodes: List[str] = None
    referral_id: Optional[int] = None  # Kim tomonidan taklif qilingan
    referrals_count: int = 0  # Nechta odam taklif qilingan
    bonus_received: int = 0  # Jami qancha bonus olgan
    
    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.used_promocodes is None:
            self.used_promocodes = []
        if self.referral_id is None:
            self.referral_id = None
        if not hasattr(self, 'referrals_count'):
            self.referrals_count = 0
        if not hasattr(self, 'bonus_received'):
            self.bonus_received = 0


@dataclass
class Order:
    order_id: int
    user_id: int
    product_key: str
    product_name: str
    price: int
    status: str = "pending"
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class UserDatabase:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.orders: List[Order] = []
        self._load_data()
    
    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for user_id, user_data in data.items():
                        if 'used_promocodes' not in user_data:
                            user_data['used_promocodes'] = []
                        if 'referral_id' not in user_data:
                            user_data['referral_id'] = None
                        if 'referrals_count' not in user_data:
                            user_data['referrals_count'] = 0
                        if 'bonus_received' not in user_data:
                            user_data['bonus_received'] = 0
                        self.users[int(user_id)] = User(**user_data)
            except (json.JSONDecodeError, FileNotFoundError):
                self.users = {}
        
        if os.path.exists(ORDERS_FILE):
            try:
                with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.orders = [Order(**order) for order in data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.orders = []
    
    def _save_users(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            data = {str(uid): asdict(user) for uid, user in self.users.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_orders(self):
        os.makedirs(os.path.dirname(ORDERS_FILE), exist_ok=True)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            data = [asdict(order) for order in self.orders]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)
    
    def create_user(self, user_id: int, username: Optional[str], full_name: str, referral_id: Optional[int] = None) -> User:
        if user_id not in self.users:
            user = User(user_id=user_id, username=username, full_name=full_name, referral_id=referral_id)
            self.users[user_id] = user
            self._save_users()
            
            # Agar referral_id bo'lsa, referral yaratuvchiga 1$ qo'shish
            if referral_id and referral_id in self.users:
                referrer = self.users[referral_id]
                referrer.balance += 1
                referrer.referrals_count += 1
                referrer.bonus_received += 1
                self._save_users()
        return self.users[user_id]
    
    def update_balance(self, user_id: int, amount: int) -> bool:
        if user_id in self.users:
            self.users[user_id].balance += amount
            self._save_users()
            return True
        return False
    
    def get_balance(self, user_id: int) -> int:
        user = self.get_user(user_id)
        return user.balance if user else 0
    
    def use_promocode(self, user_id: int, promocode: str) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        if promocode in user.used_promocodes:
            return False
        user.used_promocodes.append(promocode)
        self._save_users()
        return True
    
    def has_used_promocode(self, user_id: int, promocode: str) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        return promocode in user.used_promocodes
    
    def create_order(self, user_id: int, product_key: str, product_name: str, price: int) -> Optional[Order]:
        user = self.get_user(user_id)
        if not user or user.balance < price:
            return None
        
        order_id = len(self.orders) + 1
        order = Order(
            order_id=order_id,
            user_id=user_id,
            product_key=product_key,
            product_name=product_name,
            price=price,
            status="completed"
        )
        
        self.users[user_id].balance -= price
        self.users[user_id].total_orders += 1
        self.orders.append(order)
        
        self._save_users()
        self._save_orders()
        
        return order
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        return [order for order in self.orders if order.user_id == user_id]
    
    def get_all_users(self) -> List[User]:
        return list(self.users.values())
    
    def get_stats(self) -> Dict:
        total_users = len(self.users)
        total_orders = len(self.orders)
        total_revenue = sum(order.price for order in self.orders if order.status == "completed")
        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_revenue": total_revenue
        }


db = UserDatabase()

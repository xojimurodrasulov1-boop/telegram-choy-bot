import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_IDS = [7490733449]

SHOP_NAME = "🍵 CHOY MAGAZINE"
SHOP_DESCRIPTION = "Лучший магазин премиум чая в Ташкенте!"

PAYMENT_CARD = "8600 1234 5678 9012"
PAYMENT_CARD_HOLDER = "CHOY MAGAZINE"

SUPPORT_USERNAME = "@choy_support"
CHANNEL_USERNAME = "@choy_magazine"

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "8299312504:AAG13OG07n9Kz5f5y_BHyNZNgqGUvKitvvY")
ADMIN_IDS = [7149917323]

SHOP_NAME = "🍵 CHOY MAGAZINE"
SHOP_DESCRIPTION = "Лучший магазин премиум чая в Ташкенте!"

LTC_ADDRESS = "ltc1q4m832g9tppy0rr4tsgp8w9d020sa6gpg8ahhtu"
BTC_ADDRESS = "bc1qpe0wy0sy69gggypwslfn43w7elvxjz6hpx6rnr"

PAYMENT_CARD = "8600 1234 5678 9012"
PAYMENT_CARD_HOLDER = "CHOY MAGAZINE"

SUPPORT_USERNAME = "@choy_support"
CHANNEL_USERNAME = "@choy_magazine"
BOT_USERNAME = "store_tashkentrobot"  # Bot username referral link uchun

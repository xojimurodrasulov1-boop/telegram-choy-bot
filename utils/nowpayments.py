import aiohttp
import os
from typing import Optional, Dict, Any

NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "")
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1"


async def get_available_currencies() -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{NOWPAYMENTS_API_URL}/currencies",
            headers={"x-api-key": NOWPAYMENTS_API_KEY}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("currencies", [])
            return []


async def get_min_amount(currency: str) -> float:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{NOWPAYMENTS_API_URL}/min-amount",
            params={"currency_from": currency, "currency_to": "usd"},
            headers={"x-api-key": NOWPAYMENTS_API_KEY}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("min_amount", 0)
            return 0


async def get_estimate_price(amount_usd: float, currency: str) -> Optional[float]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{NOWPAYMENTS_API_URL}/estimate",
            params={
                "amount": amount_usd,
                "currency_from": "usd",
                "currency_to": currency
            },
            headers={"x-api-key": NOWPAYMENTS_API_KEY}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("estimated_amount")
            return None


async def create_payment(
    amount_usd: float,
    currency: str,
    order_id: str,
    order_description: str = "Balance top-up"
) -> Optional[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        payload = {
            "price_amount": amount_usd,
            "price_currency": "usd",
            "pay_currency": currency,
            "order_id": order_id,
            "order_description": order_description,
            "ipn_callback_url": "",
            "is_fixed_rate": True,
            "is_fee_paid_by_user": False
        }
        
        async with session.post(
            f"{NOWPAYMENTS_API_URL}/payment",
            json=payload,
            headers={
                "x-api-key": NOWPAYMENTS_API_KEY,
                "Content-Type": "application/json"
            }
        ) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                error = await response.text()
                print(f"NOWPayments error: {error}")
                return None


async def create_invoice(
    amount_usd: float,
    order_id: str,
    order_description: str = "Balance top-up"
) -> Optional[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        payload = {
            "price_amount": amount_usd,
            "price_currency": "usd",
            "order_id": order_id,
            "order_description": order_description,
            "success_url": "https://t.me/store_tashkentrobot",
            "cancel_url": "https://t.me/store_tashkentrobot"
        }
        
        async with session.post(
            f"{NOWPAYMENTS_API_URL}/invoice",
            json=payload,
            headers={
                "x-api-key": NOWPAYMENTS_API_KEY,
                "Content-Type": "application/json"
            }
        ) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                error = await response.text()
                print(f"NOWPayments invoice error: {error}")
                return None


async def get_payment_status(payment_id: str) -> Optional[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{NOWPAYMENTS_API_URL}/payment/{payment_id}",
            headers={"x-api-key": NOWPAYMENTS_API_KEY}
        ) as response:
            if response.status == 200:
                return await response.json()
            return None


async def check_api_status() -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{NOWPAYMENTS_API_URL}/status",
            headers={"x-api-key": NOWPAYMENTS_API_KEY}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("message") == "OK"
            return False

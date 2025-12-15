from .main_handlers import router as main_router
from .balance_handlers import router as balance_router
from .support_handlers import router as support_router

__all__ = [
    "main_router",
    "balance_router", 
    "support_router"
]

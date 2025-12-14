import random
from datetime import datetime, timedelta

REVIEW_TEXTS = [
    "четко все",
    "дома",
    "поднял",
    "классно",
    "топ товар",
    "все огонь 🔥",
    "быстро и качественно",
    "рекомендую всем",
    "супер",
    "лучший магазин",
    "все пришло",
    "доволен покупкой",
    "👍👍👍",
    "красавцы",
    "спасибо!",
    "отлично",
    "качество топ",
    "буду брать еще",
    "норм",
    "все ок",
    "без косяков",
    "5 звезд",
    "как всегда на высоте",
    "порадовали",
    "молодцы ребята",
    "все чики-пуки",
    "заебись",
    "огонь!",
    "респект",
    "лучшие",
    "взял, доволен",
    "быстрая доставка",
    "качество 👌",
    "нормально",
    "пойдет",
    "хорошо",
    "все супер",
    "рекомендую",
    "красава",
    "топчик"
]

TOTAL_REVIEWS = 15724
REVIEWS_PER_PAGE = 1
TOTAL_PAGES = 20

_cached_reviews = None
_cache_date = None


def generate_reviews(count: int = 20) -> list:
    global _cached_reviews, _cache_date
    
    today = datetime.now().date()
    
    if _cached_reviews is not None and _cache_date == today:
        return _cached_reviews
    
    reviews = []
    now = datetime.now()
    
    for i in range(count):
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        
        review_time = now.replace(hour=hours, minute=minutes)
        
        review = {
            "text": random.choice(REVIEW_TEXTS),
            "date": review_time.strftime("%d.%m.%Y"),
            "time": review_time.strftime("%H:%M"),
            "rating": "⭐⭐⭐⭐⭐"
        }
        reviews.append(review)
    
    reviews.sort(key=lambda x: x["time"], reverse=True)
    
    _cached_reviews = reviews
    _cache_date = today
    
    return reviews


def get_reviews_text(page: int = 1) -> str:
    reviews = generate_reviews(20)
    
    start_idx = (page - 1) * REVIEWS_PER_PAGE
    end_idx = start_idx + REVIEWS_PER_PAGE
    page_reviews = reviews[start_idx:end_idx]
    
    header = f"""<b>Рейтинг магазина:</b> ⭐ 4,6/5 ({TOTAL_REVIEWS} шт.)

Ваши отзывы делают наш магазин лучше!

"""
    
    reviews_text = ""
    for review in page_reviews:
        reviews_text += f"""{review['rating']}
{review['text']}
<i>от {review['date']} {review['time']}</i>

"""
    
    footer = f"\n📄 Страница {page}/{TOTAL_REVIEWS}\n\n<i>Отзывы можно оставлять только к совершенным покупкам.</i>"
    
    return header + reviews_text + footer

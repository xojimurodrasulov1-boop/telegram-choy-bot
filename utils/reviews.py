import random
import json
import os
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
TOTAL_PAGES = 15724


def load_custom_reviews():
    """Admin bot orqali qo'shilgan otzivlarni yuklash"""
    reviews_file = "data/reviews.json"
    if os.path.exists(reviews_file):
        try:
            with open(reviews_file, "r", encoding="utf-8") as f:
                reviews = json.load(f)
                # Teskari tartibda qaytarish (yangi otzivlar boshida)
                return list(reversed(reviews))
        except:
            return []
    return []


def get_reviews_text(page: int = 1) -> str:
    now = datetime.now()
    today_str = now.strftime("%d.%m.%Y")
    
    # Admin bot orqali qo'shilgan otzivlarni yuklash (yangi otzivlar boshida)
    custom_reviews = load_custom_reviews()
    
    fixed_reviews = [
        {"text": "Качество на высшем уровне! Всё как описано, быстро нашёл. Буду брать ещё 🔥", "rating": 5, "date": today_str, "time": "13:42"},
        {"text": "Отличный магазин, уже третий раз беру. Всё чётко и без проблем 👍", "rating": 5, "date": today_str, "time": "11:18"},
        {"text": "Супер! Нашёл за 2 минуты, всё на месте. Рекомендую!", "rating": 5, "date": today_str, "time": "08:55"},
        {"text": "Лучший магазин в Ташкенте! Качество топ, оператор вежливый", "rating": 5, "date": today_str, "time": "04:23"},
        {"text": "Всё пришло как надо. Спасибо за быструю работу! 💯", "rating": 5, "date": today_str, "time": "01:07"},
    ]
    
    # Custom reviews'ni boshida ko'rsatish (yangi otzivlar birinchi)
    all_reviews = custom_reviews + fixed_reviews
    
    header = f"""<b>Рейтинг магазина:</b> ⭐ 4,6/5 ({TOTAL_REVIEWS} шт.)

Ваши отзывы делают наш магазин лучше!

"""
    
    # Agar page custom reviews ichida bo'lsa
    if page <= len(all_reviews):
        review = all_reviews[page - 1]
    else:
        random.seed(page)
        review = {
            "text": random.choice(REVIEW_TEXTS),
            "rating": 5,  # Default rating
            "date": (now - timedelta(days=random.randint(1, 30))).strftime("%d.%m.%Y"),
            "time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
        }
    
    # Rating'ni olish (agar bo'lmasa, 5 deb olish)
    rating = review.get("rating", 5)
    stars = "⭐" * rating
    
    reviews_text = f"""{stars}
{review['text']}
<i>от {review['date']} {review['time']}</i>

"""
    
    footer = f"\n📄 Страница {page}/{TOTAL_REVIEWS}\n\n<i>Отзывы можно оставлять только к совершенным покупкам.</i>"
    
    return header + reviews_text + footer

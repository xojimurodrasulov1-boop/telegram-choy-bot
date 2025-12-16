#!/bin/bash
# Screen bilan botni ishga tushirish

cd "$(dirname "$0")"

# Screen session nomi
SESSION_NAME="telegram-bot"

# Agar session mavjud bo'lsa, o'chirish
screen -S $SESSION_NAME -X quit 2>/dev/null

# Yangi session yaratish va botni ishga tushirish
screen -dmS $SESSION_NAME bash -c "source venv/bin/activate && python run_both.py"

echo "✅ Bot screen session'da ishga tushdi!"
echo "📺 Session'ga kirish: screen -r $SESSION_NAME"
echo "📋 Session'larni ko'rish: screen -ls"
echo "🛑 To'xtatish: screen -S $SESSION_NAME -X quit"


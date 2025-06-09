from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get tokens from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Conversation state constants
SCAN, VOICE, FOCUS, PROMISE = range(4)

# File paths
DATA_FILE = 'reflections.json'
PROMPT_FILE = 'consultant_prompt.txt'

# OpenAI client setup
client = OpenAI(api_key=OPENAI_KEY)

# Load existing reflection data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save a new reflection entry
def save_data(user_id, entry):
    data = load_data()
    user_data = data.get(str(user_id), [])
    user_data.append(entry)
    data[str(user_id)] = user_data
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Load AI consultant prompt from file
def load_prompt():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "Ты заботливый и тёплый помощник. Отвечай с поддержкой, мягкостью и уважением."

# Utility function to truncate overly long text
def truncate(text, limit=200):
    return text if len(text) <= limit else text[:limit] + "..."

# Summarize user’s reflection history
async def history_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    entries = data.get(user_id, [])[-3:]

    if not entries:
        await update.message.reply_text("✨ Пока нет записей для анализа. Возвращайся, когда будешь готов(а) поделиться собой ✨")
        return

    history_text = "\n\n".join(
        [
            f"Дата: {entry['date']}\nЧувства: {truncate(entry.get('scan', '-'))}\nГолоса: {entry.get('voices', '-')}\nФокус: {entry.get('focus', '-')}\nОбещание: {entry.get('promise', '-')}"
            for entry in entries
        ]
    )

    summary_prompt = (
        "Проанализируй следующие записи саморефлексии. Ответь тепло, с заботой и участием, будто пишешь близкому другу.\n"
        "- Какие состояния преобладают?\n- Какие внутренние темы повторяются?\n- Что ты бы мягко порекомендовал на следующую неделю?\n"
        f"\nИстория:\n{history_text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты внимательный, тёплый и понимающий помощник. Не используй слово 'пользователь'."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=400,
            temperature=0.6
        )
        reply = response.choices[0].message.content

        lower_reply = reply.lower()
        if any(word in lower_reply for word in ["спокойствие", "покой", "уравновешенность"]):
            emoji = "🌿"
        elif any(word in lower_reply for word in ["вдохновение", "рост", "энергия"]):
            emoji = "🌞"
        elif any(word in lower_reply for word in ["тревога", "неуверенность", "напряжение"]):
            emoji = "🌧️"
        elif any(word in lower_reply for word in ["печаль", "усталость", "грусть"]):
            emoji = "🌙"
        else:
            emoji = "🪞"

        await update.message.reply_text(f"{emoji} Вот что я почувствовал(а), читая твои записи:\n\n{reply}")

    except Exception as e:
        await update.message.reply_text("⚠️ Не удалось проанализировать историю. Попробуй позже.")
        print("OpenAI summary error:", e)

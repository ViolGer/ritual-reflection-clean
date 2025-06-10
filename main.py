import logging
import shutil

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка чтения JSON: {e}")
        backup_path = DATA_FILE + ".bak"
        shutil.copy(DATA_FILE, backup_path)
        logger.warning(f"Создана резервная копия повреждённого файла: {backup_path}")
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}

# Save a new reflection entry
def save_data(user_id, entry):
    data = load_data()
    user_data = data.get(str(user_id), [])
    user_data.append(entry)
    data[str(user_id)] = user_data
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка при сохранении JSON: {e}")

# Daily reminder logic
def get_users_to_remind():
    data = load_data()
    today = date.today().isoformat()
    users_to_remind = []
    for user_id, entries in data.items():
        if not any(entry['date'].startswith(today) for entry in entries):
            users_to_remind.append(user_id)
    return users_to_remind

async def send_reminders(app):
    users = get_users_to_remind()
    for user_id in users:
        try:
            await app.bot.send_message(
                chat_id=user_id,
                text="🌙 Как прошёл день? Может, пора немного замедлиться и провести ритуал?"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить напоминание {user_id}: {e}")

# Scheduler setup
def schedule_daily_reminder(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: send_reminders(app), CronTrigger(hour=20, minute=0))
    scheduler.start()


# Load AI consultant prompt from file
def load_prompt():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "Ты заботливый и тёплый помощник. Отвечай с поддержкой, мягкостью и уважением."

# Utility function to truncate overly long text
def truncate(text, limit=200):
    return text if len(text) <= limit else text[:limit] + "..."

# Create main keyboard
MAIN_KEYBOARD = ReplyKeyboardMarkup([
    ["🌿 Начать ритуал", "🫂 Поговорить с AI"],
    ["📜 История", "❌ Отмена"]
], resize_keyboard=True)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 🌿\nЯ рядом, чтобы помочь тебе услышать себя.\n\nНажми 🌿 — чтобы начать ритуал\nИли 🫂 — чтобы просто поговорить",
        reply_markup=MAIN_KEYBOARD
    )

# Cancel the ritual
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ритуал прерван. Возвращайся, когда почувствуешь нужду ✨", reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END

# Start the ritual
async def ritual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌿 Шаг 1: Что ты сейчас чувствуешь? Как ощущается тело? Пиши свободно.")
    return SCAN

# Save body scan
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['entry'] = {
        'date': datetime.now().isoformat(),
        'scan': update.message.text
    }
    keyboard = ReplyKeyboardMarkup([
        ["Рациональный голос", "Сердце", "Вдохновитель"],
        ["Путник", "Искатель", "Берегущий отношения"],
        ["Внутренний критик", "Внутренний ребёнок"]
    ], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🗺️ Шаг 2: Какие внутренние голоса были активны на этой неделе? (Можно выбрать или написать свои через запятую)", reply_markup=keyboard)
    return VOICE

# Save voices
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['entry']['voices'] = update.message.text
    keyboard = ReplyKeyboardMarkup([
        ["Забота о теле", "Работа и цели"],
        ["Вдохновение", "Тепло в отношениях"],
        ["Спокойствие и выдох"]
    ], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🎯 Шаг 3: Какой фокус выбираешь на эту неделю? (Можно выбрать или написать свой)", reply_markup=keyboard)
    return FOCUS

# Save focus
async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['entry']['focus'] = update.message.text
    await update.message.reply_text("🤲 Шаг 4: Какое обещание хочешь дать себе на неделю?", reply_markup=ReplyKeyboardRemove())
    return PROMISE

# Save promise and end ritual
async def promise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['entry']['promise'] = update.message.text
    user_id = update.message.from_user.id
    save_data(user_id, context.user_data['entry'])
    await update.message.reply_text("✨ Ритуал завершён. Спасибо за честность и внимание к себе ✨", reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END

# Start AI talk
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🫂 Я рядом. Напиши, что на душе.")

# AI reply
async def ai_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    prompt = load_prompt()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=300,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error("OpenAI AI-talk error:", exc_info=True)
        await update.message.reply_text("⚠️ Что-то пошло не так. Попробуй позже.")

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
            max_tokens=700,
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
        await update.message.reply_text(f"{emoji} Вот что я почувствовала, читая твои записи:\n\n{reply}", reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error("OpenAI summary error:", exc_info=True)
        await update.message.reply_text("⚠️ Не удалось проанализировать историю. Попробуй позже.")

# Start the bot and add handlers
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ritual", ritual), MessageHandler(filters.Regex("^🌿 Начать ритуал$"), ritual)],
        states={
            SCAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, scan)],
            VOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, voice)],
            FOCUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, focus)],
            PROMISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, promise)],
        },
        fallbacks=[CommandHandler("cancel", cancel), MessageHandler(filters.Regex("^❌ Отмена$"), cancel)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("talk", talk))
    app.add_handler(MessageHandler(filters.Regex("^🫂 Поговорить с AI$"), talk))
    app.add_handler(MessageHandler(filters.Regex("^📜 История$"), history_summary))
    app.add_handler(CommandHandler("history", history_summary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_response))
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()

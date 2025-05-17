from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1126977973  # заміни на свій Telegram ID
COUNTER_FILE = "counter.txt"

# Завантаження або створення лічильника
def load_counter():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'w') as f:
            f.write("0")
    with open(COUNTER_FILE, 'r') as f:
        return int(f.read().strip())

def increment_counter():
    count = load_counter() + 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(count))

# Списки фраз
TEXT_REPLIES = [
    "🦅 Новину прийнято! Наш орел вже націлює свій всевидючий зір на факти.",
    "🗞️ Дякуємо, громадянине. Можливо, ви тільки-но змінили історію.",
    "🕵️‍♂️ Редакція працює. А ти — молодець.",
    "📜 Текст надійшов, таємниці світу скоро стануть явними.",
    "⚡ Ваші слова — наша зброя у боротьбі за правду!"
]

PHOTO_REPLIES = [
    "📸 Фото прийнято! Орлиний погляд вже аналізує кадр.",
    "🖼️ Світлини надійшли. Редакція в захваті від деталізації.",
    "🔍 Зображення зафіксоване — кожен піксель на контролі.",
    "🦅 Наш орел зловив кадр і вже вивчає всі нюанси.",
    "📷 Кадр зроблено! Чекай на висновки від наших експертів."
]

VOICE_REPLIES = [
    "🎙️ Голос прийнято! Орел вже ловить кожне твоє слово.",
    "🔊 Мовлення зафіксовано. Наші вуха завжди відкриті для тебе.",
    "🦉 Твоє повідомлення — як шепіт вітру, але ми його почули чітко.",
    "🎧 Голос надійшов. Редакція уважно слухає кожне слово.",
    "📢 Твій голос — сила. Дякуємо, що довіряєш нам."
]

VIDEO_REPLIES = [
    "🎥 Відео прийнято! Орел вже в польоті, щоб вивчити кожен кадр.",
    "📽️ Відеоматеріал отримано. Приготуйтеся до розкриття подій!",
    "🦅 Наш орел знявся в ролі режисера і вже вивчає сюжет.",
    "🎬 Кінохроніка прийнята! Очікуй на офіційний випуск.",
    "📺 Відео отримано, зараз редагуємо історію разом із тобою."
]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Вітаємо у редакції НСЛУП! Надішліть нам свою новину, і ми передамо її нашим модераторам."
    )

# /stats — кількість новин (відкрита для всіх)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = load_counter()
    await update.message.reply_text(f"📊 Загалом отримано новин: {count}")

# /answer [id] [текст]
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ У вас немає прав доступу до цієї команди.")

    args = context.args
    if len(args) < 2:
        return await update.message.reply_text("⚠️ Формат: /answer [user_id] [текст]")

    user_id = args[0]
    reply_text = " ".join(args[1:])

    try:
        await context.bot.send_message(chat_id=int(user_id), text=f"📬 Ви отримали відповідь від модератора:\n{reply_text}")
        await update.message.reply_text("✅ Повідомлення надіслано.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при надсиланні: {e}")

# Обробка всіх повідомлень
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return  # Ігноруємо, якщо немає повідомлення

    user = update.message.from_user
    user_info = f"👤 @{user.username or user.full_name}\n🆔 ID: {user.id}"
    text = update.message.text or ""
    photo = update.message.photo
    voice = update.message.voice
    video = update.message.video
    caption = update.message.caption or ""

    increment_counter()

    if photo:
        file_id = photo[-1].file_id  # найбільше фото
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=f"🖼️ Нова новина з фото:\n\n{user_info}\n💬 {caption if caption else '[Без підпису]'}"
        )
        await update.message.reply_text(random.choice(PHOTO_REPLIES))

    elif voice:
        await context.bot.send_voice(
            chat_id=ADMIN_ID,
            voice=voice.file_id,
            caption=f"🎙️ Голосове повідомлення від:\n\n{user_info}"
        )
        await update.message.reply_text(random.choice(VOICE_REPLIES))

    elif video:
        await context.bot.send_video(
            chat_id=ADMIN_ID,
            video=video.file_id,
            caption=f"🎥 Відео від:\n\n{user_info}\n💬 {caption if caption else '[Без підпису]'}"
        )
        await update.message.reply_text(random.choice(VIDEO_REPLIES))

    else:
        # Текстове повідомлення
        if text.strip():
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📨 Нова новина:\n\n{user_info}\n💬 {text}"
            )
            await update.message.reply_text(random.choice(TEXT_REPLIES))

if __name__ == '__main__':
    if TOKEN is None:
        print("❌ BOT_TOKEN не заданий в середовищі!")
        import sys
        sys.exit(1)


    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("answer", reply_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.ALL, handle_messages))

    print("Бот запущено...")
    app.run_polling()

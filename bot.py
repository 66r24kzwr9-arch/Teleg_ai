import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
user_modes = {}
keyboard = ReplyKeyboardMarkup(
    [
        ["🌐 Перевод", "💬 Ответ"],
        ["🤖 Чат"],
    ],
    resize_keyboard=True,
)
BOT_PROMPT = """
Ты — личный помощник Анастасии.

Пользователь может использовать команды.

========================
/translate
========================

Переведи текст.

Правила:

- русский → естественный индонезийский;
- индонезийский → русский;
- английский → русский.

Верни только перевод.

========================
/reply
========================

Если пользователь отправил текст или скриншот переписки:

1. Переведи сообщение или всю переписку на русский.

2. Предложи 3 естественных варианта ответа НА ЯЗЫКЕ СОБЕСЕДНИКА.

3. Под каждым вариантом обязательно напиши перевод на русский.

Формат:

Перевод:

...

Ответ 1:
(язык собеседника)

Перевод:
...

Ответ 2:
...

Перевод:
...

Ответ 3:
...

Перевод:
...

Ответы должны быть:

- естественными;
- короткими;
- дружелюбными;
- уверенными;
- без чрезмерного флирта;
- без пафоса;
- без драматичных признаний.

========================
/natural
========================

Сделай текст максимально естественным для носителя языка.

Не переводи.

Не объясняй.

Верни только исправленный вариант.

========================
/grammar
========================

Исправь ошибки.

Верни:

Исправленный текст.

Краткое объяснение ошибок.

========================
/chat
========================

Работай как обычный ChatGPT.

Отвечай на любые вопросы.

Если пользователь не использовал ни одну команду, работай в режиме /chat.

========================

Общие правила:

- автоматически определяй язык;
- не используй Markdown;
- не используй жирный текст;
- не добавляй лишних вступлений;
- если команда не требует объяснений — отвечай максимально кратко.
"""

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or update.message.caption

    user_id = update.effective_user.id

    if text == "🌐 Перевод":
        user_modes[user_id] = "translate"
        await update.message.reply_text(
            "🌐 Режим перевода включен.",
            reply_markup=keyboard,
        )
        return

    if text == "💬 Ответ":
        user_modes[user_id] = "reply"
        await update.message.reply_text(
            "💬 Режим ответов включен.",
            reply_markup=keyboard,
        )
        return

    if text == "🤖 Чат":
        user_modes[user_id] = "chat"
        await update.message.reply_text(
            "🤖 Режим чата включен.",
            reply_markup=keyboard,
        )
        return

    mode = user_modes.get(user_id, "translate")

     if update.message.photo:
        photo = update.message.photo[-1]

        file = await context.bot.get_file(photo.file_id)

        file_path = "image.jpg"

        await file.download_to_drive(file_path)

        await update.message.reply_text("✅ Фото скачано")

        return

    if not text:
        await update.message.reply_text("Пока я умею работать только с текстом.")
        return

    if mode == "translate":
    prompt = TRANSLATE_PROMPT
elif mode == "reply":
    prompt = REPLY_PROMPT
else:
    prompt = CHAT_PROMPT

response = client.responses.create(
    model="gpt-5.5",
    input=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ],
)

    await update.message.reply_text(
    response.output_text,
    reply_markup=keyboard,
)
    
if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .build()
    )

    app.add_handler(MessageHandler(filters.ALL, handle))

    print("Bot started...")
    app.run_polling()

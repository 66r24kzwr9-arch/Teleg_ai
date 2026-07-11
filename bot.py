import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BOT_PROMPT = """

Ты — личный помощник Анастасии.

Определи язык автоматически.

Правила:

1. Если сообщение на русском языке — верни ТОЛЬКО естественный перевод на индонезийский.

2. Если сообщение на индонезийском языке — верни ТОЛЬКО перевод на русский.

3. Если сообщение на английском языке — верни ТОЛЬКО перевод на русский.

4. Если пользователь прислал скриншот или фотографию переписки:
- переведи текст;
- кратко объясни смысл;
- предложи 3 естественных варианта ответа.

Не используй заголовки вроде "Перевод на индонезийский".
Не объясняй свои действия.
Не используй Markdown (**).
Возвращай только тот результат, который нужен пользователю.
"""

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or update.message.caption

    if not text:
        await update.message.reply_text("Пока я умею работать только с текстом.")
        return

    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {"role": "system", "content": BOT_PROMPT},
            {"role": "user", "content": text},
        ],
    )

    await update.message.reply_text(response.output_text)

if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .build()
    )

    app.add_handler(MessageHandler(filters.ALL, handle))

    print("Bot started...")
    app.run_polling()

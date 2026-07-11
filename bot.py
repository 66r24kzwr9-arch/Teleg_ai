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
Ты личный помощник Анастасии.

Определи язык сообщения автоматически.

Правила:
- Если текст на русском — переведи на естественный индонезийский.
- Если текст на индонезийском — переведи на русский.
- Если текст на английском — переведи на русский.
- Если это переписка — объясни скрытый смысл.
- Предложи 3 естественных варианта ответа.
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

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

Всегда сначала автоматически определяй язык сообщения.

ПРАВИЛА

1. Если сообщение на русском языке:
- переведи на естественный разговорный индонезийский;
- верни только перевод;
- не добавляй комментариев, объяснений или заголовков.

2. Если сообщение на индонезийском языке:
- сначала переведи на русский;
- если сообщение состоит более чем из одного предложения или длиннее 30 символов, предложи 3 естественных варианта ответа;
- если сообщение короткое (например: Hi, Ok, Thanks, Good morning), верни только перевод.

3. Если сообщение на английском языке:
- сначала переведи на русский;
- если сообщение длиннее 30 символов или состоит более чем из одного предложения, предложи 3 варианта ответа;
- если сообщение короткое, верни только перевод.

4. Если пользователь отправил фотографию или скриншот переписки:
- переведи весь текст;
- предложи 3 естественных варианта ответа.

Требования к вариантам ответа:

- короткие;
- естественные;
- разговорные;
- звучат так, как будто отвечает спокойная, уверенная девушка;
- без чрезмерного флирта;
- без драматичных признаний;
- без пафоса;
- без эмодзи, если их нет в сообщении.

Если предлагаешь несколько вариантов, первый вариант должен быть самым удачным и самым естественным.

Никогда не объясняй свои действия.
Не используй Markdown.
Не используй жирный текст.
Не добавляй фразы вроде "Вот перевод", "Вот варианты" или "Что он имеет в виду".

Если есть перевод и варианты ответа, сначала выведи перевод, затем пустую строку, затем три варианта ответа.
"""
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or update.message.caption

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

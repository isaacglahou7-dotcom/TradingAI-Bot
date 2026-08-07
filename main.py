from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import asyncio
import os

from aiohttp import web
from huggingface_hub import InferenceClient


# =========================
# VARIABLES
# =========================

TOKEN = os.getenv("BOT_TOKEN", "").replace("\n", "").replace("\r", "").strip()

HF_TOKEN = os.getenv("HF_TOKEN", "").replace("\n", "").replace("\r", "").strip()


if not TOKEN:
    raise ValueError("❌ BOT_TOKEN manquant dans Render")

if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN manquant dans Render")


# Client IA Hugging Face

client = InferenceClient(
    token=HF_TOKEN
)


# =========================
# COMMAND START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Trading AI Bot en ligne !\n\n"
        "📸 Envoie-moi ton graphique.\n\n"
        "Je vais analyser :\n"
        "📈 Tendance\n"
        "🎯 Entrée\n"
        "🛑 Stop Loss\n"
        "✅ Take Profit\n"
        "📊 Confiance"
    )


# =========================
# ANALYSE IMAGE
# =========================

async def analyse_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 Image reçue !\n\n"
        "🔎 Analyse IA en cours..."
    )


    photo = update.message.photo[-1]


    file = await context.bot.get_file(photo.file_id)


    image_path = "graphique.png"


    await file.download_to_drive(image_path)


    try:

        image = Image.open(image_path)


        prompt = """
Analyse cette capture de graphique de trading.

Donne une analyse professionnelle :

- Actif détecté
- Tendance actuelle
- Support et résistance
- Signal BUY ou SELL
- Prix d'entrée estimé
- Stop Loss
- TP1 TP2 TP3
- Ratio risque/rendement
- Niveau de confiance en %

Réponds en français avec un format clair.
"""


        # Analyse IA (modèle vision à définir)

        result = client.chat_completion(
            model="Qwen/Qwen2.5-VL-7B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "image": image
                        }
                    ]
                }
            ]
        )


        response = result.choices[0].message.content


        await update.message.reply_text(
            "🧠 ANALYSE IA :\n\n" + response
        )


    except Exception as e:

        await update.message.reply_text(
            f"❌ Erreur analyse IA :\n{e}"
        )


# =========================
# PORT RENDER
# =========================

async def health_check(request):

    return web.Response(
        text="Trading AI Bot OK"
    )


async def start_web_server():

    app_web = web.Application()

    app_web.router.add_get(
        "/",
        health_check
    )


    runner = web.AppRunner(app_web)

    await runner.setup()


    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )


    await site.start()



# =========================
# TELEGRAM
# =========================

app = ApplicationBuilder().token(TOKEN).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    MessageHandler(
        filters.PHOTO,
        analyse_image
    )
)



async def main():

    print("🤖 Bot démarré...")


    await start_web_server()


    await app.initialize()

    await app.start()

    await app.updater.start_polling()


    await asyncio.Event().wait()



if __name__ == "__main__":

    asyncio.run(main())

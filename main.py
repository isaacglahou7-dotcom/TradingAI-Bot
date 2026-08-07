from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import asyncio
import os

from aiohttp import web
from huggingface_hub import InferenceClient
from PIL import Image


# =========================
# VARIABLES
# =========================

TOKEN = os.getenv("BOT_TOKEN", "").replace("\n", "").replace("\r", "").strip()

HF_TOKEN = os.getenv("HF_TOKEN", "").replace("\n", "").replace("\r", "").strip()


if not TOKEN:
    raise ValueError("❌ BOT_TOKEN manquant dans Render")

if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN manquant dans Render")


client = InferenceClient(
    token=HF_TOKEN
)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Trading AI Bot en ligne !\n\n"
        "📸 Envoie ton graphique.\n\n"
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


        await update.message.reply_text(
            "🖼️ Image chargée.\n"
            "🧠 Interrogation du modèle IA..."
        )


        prompt = """
Tu es un analyste professionnel Forex.

Analyse ce graphique de trading.

Donne :

📌 Actif détecté
📈 Tendance
📊 Structure du marché
🟢 BUY ou 🔴 SELL
🎯 Zone d'entrée
🛑 Stop Loss
✅ TP1
✅ TP2
📈 Confiance en %

Réponds en français.
"""


        # Préparation image pour IA

        result = client.image_to_text(
            image,
            model="Salesforce/blip-image-captioning-large"
        )


        description = result[0].generated_text


        analyse = f"""
📊 ANALYSE IA TRADING

{description}


⚠️ Analyse graphique avancée en préparation.
Le modèle vision actuel sert de base.
"""


        await update.message.reply_text(analyse)


    except Exception as e:

        await update.message.reply_text(
            f"❌ Erreur IA :\n{e}"
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

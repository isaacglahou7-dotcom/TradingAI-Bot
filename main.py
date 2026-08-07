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
        "📸 Envoie-moi ton graphique.\n\n"
        "Je vais analyser :\n"
        "📈 Tendance\n"
        "🎯 Entrée\n"
        "🛑 Stop Loss\n"
        "✅ Take Profit\n"
        "📊 Confiance"
    )


# =========================
# IMAGE ANALYSE
# =========================

async def analyse_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 Image reçue !\n\n"
        "🔎 Téléchargement du graphique..."
    )


    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    image_path = "graphique.png"


    await file.download_to_drive(image_path)


    await update.message.reply_text(
        "✅ Graphique enregistré.\n\n"
        "🧠 Préparation analyse IA..."
    )


    try:

        image = Image.open(image_path)


        await update.message.reply_text(
            "🔍 Image chargée correctement.\n"
            "🤖 Connexion IA en préparation..."
        )


        # Analyse IA sera activée ici


    except Exception as e:

        await update.message.reply_text(
            f"❌ Erreur analyse image :\n{e}"
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

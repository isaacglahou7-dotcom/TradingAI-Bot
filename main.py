from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import asyncio
import os

from aiohttp import web

from config import BOT_TOKEN, PORT, check_config
from vision import analyse_graphique


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Trading AI Bot PRO en ligne !\n\n"
        "📸 Envoie ton graphique.\n\n"
        "Je vais analyser :\n"
        "📈 Tendance\n"
        "🟢 BUY / 🔴 SELL\n"
        "🎯 Entrée\n"
        "🛑 Stop Loss\n"
        "✅ TP1 / TP2 / TP3\n"
        "📊 Confiance"
    )


# =========================
# IMAGE
# =========================

async def analyse_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📸 Graphique reçu.\n\n"
        "🧠 Analyse IA en préparation..."
    )


    try:

        photo = update.message.photo[-1]

        file = await context.bot.get_file(
            photo.file_id
        )


        image_path = "graphique.png"


        await file.download_to_drive(
            image_path
        )


        await update.message.reply_text(
            "🔍 Image chargée.\n"
            "📊 Analyse du marché..."
        )


        resultat = await analyse_graphique(
            image_path
        )


        await update.message.reply_text(
            resultat
        )


    except Exception as e:

        await update.message.reply_text(
            "❌ Erreur analyse :\n"
            f"{type(e).__name__}\n"
            f"{str(e)}"
        )



# =========================
# PORT RENDER
# =========================

async def health(request):

    return web.Response(
        text="Trading AI Bot PRO OK"
    )


async def start_server():

    server = web.Application()

    server.router.add_get(
        "/",
        health
    )


    runner = web.AppRunner(
        server
    )

    await runner.setup()


    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT
    )

    await site.start()



# =========================
# TELEGRAM
# =========================

app = ApplicationBuilder().token(
    BOT_TOKEN
).build()


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

    check_config()

    print(
        "🤖 Trading AI Bot PRO démarré..."
    )


    await start_server()


    await app.initialize()

    await app.start()

    await app.updater.start_polling()


    await asyncio.Event().wait()



if __name__ == "__main__":

    asyncio.run(main())

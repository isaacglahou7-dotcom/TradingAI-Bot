from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import asyncio
import os

from aiohttp import web


TOKEN = os.getenv("BOT_TOKEN", "").replace("\n", "").replace("\r", "").strip()

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN manquant dans les variables Render")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Trading AI Bot en ligne !\n\n"
        "📸 Envoie-moi une capture de ton graphique.\n"
        "Je vais analyser la tendance, l'entrée, le SL et les TP."
    )


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
        "🧠 Prêt pour l'analyse IA."
    )


# =========================
# SERVEUR POUR RENDER
# =========================

async def health_check(request):
    return web.Response(text="Trading AI Bot OK")


async def start_web_server():
    app_web = web.Application()

    app_web.router.add_get("/", health_check)

    runner = web.AppRunner(app_web)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()


# =========================
# TELEGRAM BOT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(filters.PHOTO, analyse_image)
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

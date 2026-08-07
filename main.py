from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

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
        "🔎 Analyse du graphique en cours..."
    )

    # Intelligence artificielle sera ajoutée ici


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.PHOTO, analyse_image)
)


async def main():
    print("🤖 Bot démarré...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

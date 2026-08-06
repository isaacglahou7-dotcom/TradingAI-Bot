from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "TON_TOKEN_BOTFATHER"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Trading AI Bot en ligne !\n\n"
        "📸 Envoie-moi une capture de ton graphique.\n"
        "Je vais analyser la tendance, l'entrée, le SL et les TP."
    )


async def analyse_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]

    await update.message.reply_text(
        "📊 Image reçue !\n\n"
        "🔎 Analyse du graphique en cours..."
    )

    # On ajoutera ici l'intelligence artificielle


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.PHOTO, analyse_image)
)

print("🤖 Bot démarré...")

app.run_polling()

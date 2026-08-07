import os


# =========================
# TELEGRAM
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()


# =========================
# GEMINI IA
# =========================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# =========================
# RENDER
# =========================

PORT = int(
    os.getenv(
        "PORT",
        10000
    )
)


def check_config():

    if not BOT_TOKEN:
        raise ValueError(
            "❌ BOT_TOKEN manquant"
        )


    if not GEMINI_API_KEY:
        raise ValueError(
            "❌ GEMINI_API_KEY manquant"
        )

import os


# =========================
# CONFIGURATION BOT
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()


# =========================
# IA
# =========================

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()


# =========================
# RENDER
# =========================

PORT = int(os.getenv("PORT", 10000))


def check_config():

    if not BOT_TOKEN:
        raise ValueError(
            "❌ BOT_TOKEN manquant dans Render"
        )

    if not HF_TOKEN:
        raise ValueError(
            "❌ HF_TOKEN manquant dans Render"
        )

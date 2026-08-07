import os


# =========================
# TELEGRAM
# =========================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
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
            "❌ BOT_TOKEN manquant dans Render"
        )

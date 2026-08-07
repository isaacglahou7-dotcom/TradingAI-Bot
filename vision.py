import base64
import requests

from config import HF_TOKEN
from trading import format_analyse


# =========================
# ANALYSE IMAGE IA
# =========================

async def analyse_graphique(image_path):

    try:

        with open(
            image_path,
            "rb"
        ) as image_file:

            image_bytes = image_file.read()


        image_base64 = base64.b64encode(
            image_bytes
        ).decode()


        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }


        payload = {

            "inputs": image_base64,

            "parameters": {

                "prompt":
                """
Tu es un analyste Forex professionnel.

Analyse ce graphique.

Donne :

- Actif
- Tendance
- BUY ou SELL
- Zone d'entrée
- Stop Loss
- TP1 TP2 TP3
- Confiance %
- Raisons techniques

Réponds en français.
"""
            }
        }


        response = requests.post(

            "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-VL-7B-Instruct",

            headers=headers,

            json=payload,

            timeout=60
        )


        data = response.json()


        if isinstance(data, dict) and "error" in data:

            return (
                "⚠️ IA indisponible actuellement.\n\n"
                + data["error"]
            )


        return format_analyse(
            str(data)
        )


    except Exception as e:

        return (
            "❌ Erreur moteur vision :\n"
            f"{type(e).__name__}\n"
            f"{str(e)}"
        )

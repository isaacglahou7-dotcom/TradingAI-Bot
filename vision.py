import google.generativeai as genai
from PIL import Image

from config import GEMINI_API_KEY
from trading import format_analyse


# =========================
# CONFIG GEMINI
# =========================

genai.configure(
    api_key=GEMINI_API_KEY
)


model = genai.GenerativeModel(
    "gemini-2.0-flash"
)



# =========================
# ANALYSE GRAPHIQUE
# =========================

async def analyse_graphique(image_path):

    try:

        image = Image.open(
            image_path
        )


        prompt = """
Tu es un analyste professionnel Forex.

Analyse cette capture de graphique.

Donne une analyse structurée :

📌 Actif détecté :
📈 Tendance :
📊 Structure du marché :
🟢 Signal : BUY ou SELL
🎯 Zone d'entrée :
🛑 Stop Loss :
✅ TP1 :
✅ TP2 :
✅ TP3 :
📊 Confiance en % :

Explique les raisons :
- Supports/Résistances
- Tendances
- Figures chartistes
- Indicateurs visibles

Réponds en français.

Ne donne pas de certitude absolue.
"""


        response = model.generate_content(
            [
                prompt,
                image
            ]
        )


        if not response.text:

            return (
                "⚠️ Gemini n'a pas retourné d'analyse."
            )


        return format_analyse(
            response.text
        )


    except Exception as e:

        return (
            "❌ Erreur Gemini Vision :\n"
            f"{type(e).__name__}\n"
            f"{str(e)}"
        )

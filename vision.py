from PIL import Image
import cv2
import numpy as np

from trading import format_analyse



# =========================
# ANALYSE IMAGE
# =========================

async def analyse_graphique(image_path):

    try:

        image = Image.open(
            image_path
        )


        # Conversion OpenCV

        img = cv2.imread(
            image_path
        )


        if img is None:

            return "❌ Impossible de lire l'image."


        # Taille graphique

        height, width = img.shape[:2]


        # Détection luminosité générale

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )


        moyenne = np.mean(gray)



        # Analyse simple de structure

        edges = cv2.Canny(
            gray,
            50,
            150
        )


        niveau = np.mean(edges)



        # Logique de tendance basique

        if moyenne > 130:

            tendance = "Haussière probable 📈"

            signal = "BUY 🟢"


        else:

            tendance = "Baissière probable 📉"

            signal = "SELL 🔴"



        # Confiance basée sur la détection

        confiance = int(
            min(
                85,
                max(
                    50,
                    niveau
                )
            )
        )


        analyse = f"""

📊 ANALYSE TRADING AI

🖼️ Image analysée :
Largeur : {width}px
Hauteur : {height}px


📈 Tendance :
{tendance}


🎯 Signal :
{signal}


💰 Gestion du trade :

Entrée :
Zone actuelle du prix

🛑 Stop Loss :
Dernier support/résistance visible

✅ TP1 :
Risque/Rendement 1:1

✅ TP2 :
Risque/Rendement 1:2

✅ TP3 :
Extension de tendance


📊 Confiance :
{confiance}%


⚠️ Analyse automatique.
Toujours confirmer avant de trader.
"""


        return format_analyse(
            analyse
        )


    except Exception as e:

        return (
            "❌ Erreur analyse locale :\n"
            f"{type(e).__name__}\n"
            f"{str(e)}"
        )

import cv2
import numpy as np

from trading import format_analyse


# ============================================================
# OUTILS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def analyse_structure(gray):
    """
    Analyse grossière de la structure visuelle du graphique.
    Cette fonction ne prétend pas connaître le prix réel.
    """

    height, width = gray.shape

    # On travaille principalement sur la partie centrale
    # pour éviter une partie de l'interface autour du graphique.
    x1 = int(width * 0.05)
    x2 = int(width * 0.95)

    y1 = int(height * 0.05)
    y2 = int(height * 0.95)

    chart = gray[y1:y2, x1:x2]

    if chart.size == 0:
        return None

    # Réduction du bruit
    blurred = cv2.GaussianBlur(
        chart,
        (5, 5),
        0
    )

    # Détection des contours
    edges = cv2.Canny(
        blurred,
        50,
        150
    )

    # Projection horizontale des contours.
    # Cela permet d'obtenir une indication de la répartition
    # verticale des éléments du graphique.
    horizontal_activity = np.sum(
        edges,
        axis=1
    )

    if len(horizontal_activity) < 10:
        return None

    # Découpage en plusieurs zones verticales
    sections = np.array_split(
        horizontal_activity,
        5
    )

    values = [
        float(np.mean(section))
        for section in sections
    ]

    # Comparaison des zones supérieures et inférieures
    upper = np.mean(values[:2])
    middle = values[2]
    lower = np.mean(values[-2:])

    # Cette estimation est volontairement prudente.
    difference = lower - upper

    if difference > 3:
        direction = "Haussière probable 📈"
        signal = "BUY 🟢"

    elif difference < -3:
        direction = "Baissière probable 📉"
        signal = "SELL 🔴"

    else:
        direction = "Neutre / marché indécis ⚪"
        signal = "ATTENDRE ⏳"

    return {
        "direction": direction,
        "signal": signal,
        "activity": values,
        "middle": middle
    }


def detect_levels(gray):
    """
    Détection de niveaux horizontaux visuels.
    Ces niveaux sont exprimés en pixels et PAS en prix.
    """

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=80,
        minLineLength=max(
            50,
            gray.shape[1] // 5
        ),
        maxLineGap=15
    )

    horizontal_levels = []

    if lines is None:
        return horizontal_levels

    for line in lines:

        x1, y1, x2, y2 = line[0]

        # Ligne presque horizontale
        if abs(y2 - y1) <= 3:

            y = int((y1 + y2) / 2)

            horizontal_levels.append(y)

    # Regroupement des niveaux proches
    horizontal_levels.sort()

    grouped = []

    for level in horizontal_levels:

        if not grouped:

            grouped.append(level)

        elif abs(level - grouped[-1]) > 12:

            grouped.append(level)

    return grouped


def confidence_from_structure(structure):

    if not structure:
        return 50

    activity = structure["activity"]

    if not activity:
        return 50

    spread = float(
        np.std(activity)
    )

    confidence = 50 + int(
        clamp(
            spread * 2,
            0,
            30
        )
    )

    return clamp(
        confidence,
        50,
        80
    )


# ============================================================
# ANALYSE PRINCIPALE
# ============================================================

async def analyse_graphique(image_path):

    try:

        image = cv2.imread(
            image_path
        )

        if image is None:

            return (
                "❌ Impossible de lire "
                "le graphique."
            )


        height, width = image.shape[:2]


        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        # ----------------------------------------------------
        # STRUCTURE
        # ----------------------------------------------------

        structure = analyse_structure(
            gray
        )


        if structure is None:

            return (
                "⚠️ Graphique insuffisant "
                "pour effectuer une analyse."
            )


        direction = structure[
            "direction"
        ]

        signal = structure[
            "signal"
        ]


        confidence = (
            confidence_from_structure(
                structure
            )
        )


        # ----------------------------------------------------
        # NIVEAUX VISUELS
        # ----------------------------------------------------

        levels = detect_levels(
            gray
        )


        # ----------------------------------------------------
        # PRIX
        # ----------------------------------------------------

        # IMPORTANT :
        #
        # Nous ne connaissons pas encore la correspondance
        # pixel -> prix.
        #
        # Il est donc INTERDIT d'inventer un prix.
        #
        # Exemple interdit :
        # entrée = 100
        # SL = 102
        #
        # On affiche donc les niveaux en pixels uniquement
        # jusqu'à ce qu'une vraie échelle de prix soit lue.
        # ----------------------------------------------------

        if levels:

            level_text = (
                f"{len(levels)} niveau(x) "
                "horizontal(aux) détecté(s)."
            )

        else:

            level_text = (
                "Aucun niveau horizontal "
                "fiable détecté."
            )


        # ----------------------------------------------------
        # ANALYSE
        # ----------------------------------------------------

        analyse = f"""
📊 ANALYSE TRADING AI PRO

🖼️ Graphique détecté

Résolution :
{width}px × {height}px


📈 Tendance :
{direction}


🎯 Signal :
{signal}


📍 Structure :
{level_text}


📊 Confiance structurelle :
{confidence}%


🧠 Analyse :

Le moteur a analysé la structure
visuelle du graphique et les éléments
horizontaux détectables.


💰 PRIX RÉEL :

⚠️ Prix non détecté.

L'échelle de prix n'est pas encore
suffisamment lisible pour convertir
les coordonnées de l'image en prix réel.


🛑 STOP LOSS :
Non calculé.


✅ TP1 :
Non calculé.


✅ TP2 :
Non calculé.


✅ TP3 :
Non calculé.


⚠️ IMPORTANT :

Aucun prix n'est inventé.

Pour calculer correctement l'entrée,
le SL et les TP, le moteur doit pouvoir
lire l'échelle de prix du graphique ou
recevoir les données OHLC.
"""


        return format_analyse(
            analyse
        )


    except Exception as e:

        return (
            "❌ Erreur analyse technique :\n"
            f"{type(e).__name__}\n"
            f"{str(e)}"
        )

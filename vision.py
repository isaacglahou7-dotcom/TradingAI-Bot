import cv2
import numpy as np
from trading import format_analyse
# ============================================================
# OUTILS
# ============================================================
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))
# ============================================================
# ANALYSE DE STRUCTURE
# ============================================================
def analyse_structure(gray):
    height, width = gray.shape
    x1 = int(width * 0.05)
    x2 = int(width * 0.95)
    y1 = int(height * 0.05)
    y2 = int(height * 0.95)
    chart = gray[y1:y2, x1:x2]
    if chart.size == 0:
        return None
    blurred = cv2.GaussianBlur(
        chart,
        (5, 5),
        0
    )
    edges = cv2.Canny(
        blurred,
        50,
        150
    )
    horizontal_activity = np.sum(
        edges,
        axis=1
    )
    if len(horizontal_activity) < 10:
        return None
    sections = np.array_split(
        horizontal_activity,
        5
    )
    values = [
        float(np.mean(section))
        for section in sections
    ]
    upper = float(
        np.mean(values[:2])
    )
    middle = float(
        values[2]
    )
    lower = float(
        np.mean(values[-2:])
    )
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
# ============================================================
# DETECTION DES NIVEAUX
# ============================================================
def detect_levels(gray):
    edges = cv2.Canny(
        gray,
        50,
        150
    )
    min_line_length = max(
        50,
        gray.shape[1] // 5
    )
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=80,
        minLineLength=min_line_length,
        maxLineGap=15
    )
    horizontal_levels = []
    if lines is None:
        return horizontal_levels
    # Convertit proprement le résultat OpenCV
    # en tableau de lignes.
    lines = np.asarray(lines)
    try:
        # Format classique :
        # (N, 1, 4)
        if lines.ndim == 3:
            lines = lines.reshape(
                -1,
                4
            )
        # Autre format possible :
        # (N, 4)
        elif lines.ndim == 2:
            if lines.shape[1] != 4:
                return horizontal_levels
        else:
            return horizontal_levels
        for line in lines:
            if len(line) != 4:
                continue
            x1, y1, x2, y2 = [
                int(value)
                for value in line
            ]
            # Ligne presque horizontale
            if abs(y2 - y1) <= 3:
                y = int(
                    (y1 + y2) / 2
                )
                horizontal_levels.append(
                    y
                )
    except Exception:
        return horizontal_levels
    horizontal_levels.sort()
    grouped = []
    for level in horizontal_levels:
        if not grouped:
            grouped.append(level)
        elif abs(
            level - grouped[-1]
        ) > 12:
            grouped.append(level)
    return grouped
# ============================================================
# CONFIANCE
# ============================================================
def confidence_from_structure(
    structure
):
    if not structure:
        return 50
    activity = structure.get(
        "activity",
        []
    )
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
    return int(
        clamp(
            confidence,
            50,
            80
        )
    )
# ============================================================
# ANALYSE PRINCIPALE
# ============================================================
async def analyse_graphique(
    image_path
):
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
        direction = structure.get(
            "direction",
            "Indéterminée"
        )
        signal = structure.get(
            "signal",
            "ATTENDRE ⏳"
        )
        confidence = (
            confidence_from_structure(
                structure
            )
        )
        # ----------------------------------------------------
        # NIVEAUX
        # ----------------------------------------------------
        levels = detect_levels(
            gray
        )
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
        # RESULTAT
        # ----------------------------------------------------
        analyse = f"""
📊 ANALYSE TRADING AI PRO
🖼️ GRAPHIQUE
Résolution :
{width}px × {height}px
📈 TENDANCE
{direction}
🎯 SIGNAL
{signal}
📍 STRUCTURE
{level_text}
📊 CONFIANCE STRUCTURELLE
{confidence}%
🧠 ANALYSE TECHNIQUE
Le moteur a analysé :
• Structure visuelle
• Activité du graphique
• Niveaux horizontaux
• Direction probable
💰 PRIX RÉEL
⚠️ Prix non détecté.
L'échelle de prix doit encore être
lue correctement avant de calculer
un prix d'entrée réel.
🛑 STOP LOSS
Non calculé.
✅ TP1
Non calculé.
✅ TP2
Non calculé.
✅ TP3
Non calculé.
⚠️ IMPORTANT
Aucun prix fictif n'est utilisé.
Le bot ne donnera pas de SL ou TP
tant qu'il ne peut pas déterminer
le prix réel du graphique.
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

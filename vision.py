import cv2
import numpy as np
import pytesseract
import re

from trading import (
    format_analyse,
    format_price,
    calculate_trade_levels
)


# ============================================================
# OCR
# ============================================================

def clean_ocr_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def ocr_image(image):
    """
    OCR général.
    Si Tesseract n'est pas disponible sur Render,
    on retourne simplement une chaîne vide.
    """

    try:
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        gray = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY +
            cv2.THRESH_OTSU
        )[1]

        text = pytesseract.image_to_string(
            gray,
            config="--psm 11"
        )

        return clean_ocr_text(text)

    except Exception:
        return ""


# ============================================================
# SYMBOLE
# ============================================================

def detect_symbol(text):

    if not text:
        return "Non détecté"

    symbols = [
        "XAUUSD",
        "XAU/USD",
        "BTCUSD",
        "BTC/USD",
        "EURUSD",
        "EUR/USD",
        "GBPUSD",
        "GBP/USD",
        "USDJPY",
        "USD/JPY",
        "US30",
        "NAS100",
        "NASDAQ",
        "SPX500",
        "ETHUSD"
    ]

    upper = text.upper()

    for symbol in symbols:

        if symbol in upper:
            return symbol

    return "Non détecté"


# ============================================================
# TIMEFRAME
# ============================================================

def detect_timeframe(text):

    if not text:
        return "Non détecté"

    upper = text.upper()

    patterns = [
        r"\bM1\b",
        r"\bM3\b",
        r"\bM5\b",
        r"\bM15\b",
        r"\bM30\b",
        r"\bH1\b",
        r"\bH2\b",
        r"\bH4\b",
        r"\bH6\b",
        r"\bH8\b",
        r"\bD1\b",
        r"\bW1\b",
        r"\bMN1\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            upper
        )

        if match:
            return match.group(0)

    return "Non détecté"


# ============================================================
# NOMBRES OCR
# ============================================================

def extract_numbers(text):

    if not text:
        return []

    matches = re.findall(
        r"(?<![A-Za-z])"
        r"\d{1,7}"
        r"(?:[.,]\d{1,6})?"
        r"(?![A-Za-z])",
        text
    )

    numbers = []

    for value in matches:

        try:

            value = value.replace(
                ",",
                "."
            )

            number = float(value)

            if number > 0:
                numbers.append(number)

        except Exception:
            continue

    return numbers


# ============================================================
# ECHELLE DE PRIX
# ============================================================

def read_price_scale(image):

    height, width = image.shape[:2]

    # On examine principalement le côté droit.
    # TradingView / MT5 affichent généralement
    # l'échelle de prix sur cette zone.

    x1 = int(width * 0.78)

    right_side = image[
        :,
        x1:
    ]

    text = ""

    try:

        gray = cv2.cvtColor(
            right_side,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.resize(
            gray,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_CUBIC
        )

        gray = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY +
            cv2.THRESH_OTSU
        )[1]

        text = pytesseract.image_to_string(
            gray,
            config="--psm 6"
        )

    except Exception:

        return []

    numbers = extract_numbers(text)

    # Suppression des doublons
    result = []

    for number in numbers:

        if not result:

            result.append(number)

        elif abs(number - result[-1]) > 0.000001:

            result.append(number)

    return result


# ============================================================
# DETECTION DES CHANDELIERS
# ============================================================

def detect_candles(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candle_candidates = []

    height, width = gray.shape

    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )

        # Filtrage des petits éléments
        if w < 2 or h < 5:
            continue

        # Filtrage des éléments gigantesques
        if w > width * 0.10:
            continue

        if h > height * 0.50:
            continue

        ratio = h / max(w, 1)

        # Forme verticale typique
        if ratio >= 1.2:

            candle_candidates.append(
                {
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h
                }
            )

    # Tri de gauche à droite
    candle_candidates.sort(
        key=lambda item: item["x"]
    )

    return candle_candidates


# ============================================================
# STRUCTURE HH / HL / LH / LL
# ============================================================

def detect_structure(candles):

    if len(candles) < 6:

        return {
            "structure": "Indéterminée",
            "direction": "NEUTRE",
            "signal": "ATTENDRE ⏳"
        }

    recent = candles[-20:]

    highs = [
        c["y"]
        for c in recent
    ]

    lows = [
        c["y"] + c["h"]
        for c in recent
    ]

    # Dans une image :
    # y plus petit = plus haut
    # y plus grand = plus bas

    first_high = np.mean(
        highs[:len(highs)//2]
    )

    last_high = np.mean(
        highs[len(highs)//2:]
    )

    first_low = np.mean(
        lows[:len(lows)//2]
    )

    last_low = np.mean(
        lows[len(lows)//2:]
    )

    higher_high = last_high < first_high
    higher_low = last_low < first_low

    lower_high = last_high > first_high
    lower_low = last_low > first_low


    if higher_high and higher_low:

        return {
            "structure": "HH / HL",
            "direction": "HAUSSIÈRE",
            "signal": "BUY 🟢"
        }


    if lower_high and lower_low:

        return {
            "structure": "LH / LL",
            "direction": "BAISSIÈRE",
            "signal": "SELL 🔴"
        }


    if higher_high:

        return {
            "structure": "HH",
            "direction": "HAUSSIÈRE",
            "signal": "BUY 🟢"
        }


    if lower_low:

        return {
            "structure": "LL",
            "direction": "BAISSIÈRE",
            "signal": "SELL 🔴"
        }


    return {
        "structure": "Structure mixte",
        "direction": "NEUTRE",
        "signal": "ATTENDRE ⏳"
    }


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def detect_support_resistance(
    image,
    candles
):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=70,
        minLineLength=max(
            80,
            image.shape[1] // 5
        ),
        maxLineGap=20
    )

    levels = []

    if lines is not None:

        lines = np.asarray(
            lines
        ).reshape(
            -1,
            4
        )

        for line in lines:

            x1, y1, x2, y2 = [
                int(v)
                for v in line
            ]

            if abs(y2 - y1) <= 4:

                y = int(
                    (y1 + y2) / 2
                )

                levels.append(y)

    # Ajouter également les zones extrêmes
    # des derniers chandeliers.

    if candles:

        recent = candles[-20:]

        for candle in recent:

            levels.append(
                int(candle["y"])
            )

            levels.append(
                int(
                    candle["y"] +
                    candle["h"]
                )
            )

    levels.sort()

    grouped = []

    for level in levels:

        if not grouped:

            grouped.append(level)

        elif abs(
            level - grouped[-1]
        ) > 15:

            grouped.append(level)

    if not grouped:

        return None, None, []


    # Prix visuel actuel = zone du dernier chandelier
    last = candles[-1] if candles else None

    if last:

        current_y = (
            last["y"] +
            last["h"] / 2
        )

    else:

        current_y = image.shape[0] / 2


    supports = [
        level
        for level in grouped
        if level > current_y
    ]

    resistances = [
        level
        for level in grouped
        if level < current_y
    ]


    support = (
        min(
            supports,
            key=lambda x: abs(
                x - current_y
            )
        )
        if supports
        else None
    )


    resistance = (
        min(
            resistances,
            key=lambda x: abs(
                x - current_y
            )
        )
        if resistances
        else None
    )


    return (
        support,
        resistance,
        grouped
    )


# ============================================================
# BREAKOUT / REJET
# ============================================================

def detect_breakout_rejection(
    candles,
    support,
    resistance
):

    if len(candles) < 5:

        return "Aucun breakout/rejet confirmé"

    recent = candles[-5:]

    last = recent[-1]

    current_center = (
        last["y"] +
        last["h"] / 2
    )

    previous_centers = [
        c["y"] + c["h"] / 2
        for c in recent[:-1]
    ]

    previous_average = np.mean(
        previous_centers
    )


    # Comme y augmente vers le bas :
    # déplacement vers le haut = baisse de y

    if resistance is not None:

        if (
            current_center <
            resistance
            and
            previous_average >= resistance
        ):

            return "🔥 Breakout haussier probable"


    if support is not None:

        if (
            current_center >
            support
            and
            previous_average <= support
        ):

            return "🔥 Breakout baissier probable"


    # Rejet visuel
    if resistance is not None:

        distance = abs(
            current_center -
            resistance
        )

        if distance < 20:

            return "↩️ Rejet possible de résistance"


    if support is not None:

        distance = abs(
            current_center -
            support
        )

        if distance < 20:

            return "↩️ Rejet possible du support"


    return "Aucun breakout/rejet confirmé"


# ============================================================
# CONVERSION PIXEL → PRIX
# ============================================================

def convert_pixel_to_price(
    pixel_y,
    image_height,
    prices
):
    """
    Conversion très prudente.

    Nous avons besoin d'au moins deux prix
    provenant de l'échelle.

    Sans correspondance fiable entre les positions
    des textes OCR et les prix, on refuse de créer
    un prix artificiel.
    """

    if len(prices) < 2:

        return None

    prices = sorted(
        set(prices)
    )

    if len(prices) < 2:

        return None

    # On n'utilise cette conversion que si les prix
    # sont suffisamment proches pour représenter
    # une même échelle.

    low = prices[0]
    high = prices[-1]

    if high <= low:

        return None

    # Estimation verticale globale.
    # Ce n'est PAS considérée comme une lecture exacte.
    ratio = 1 - (
        pixel_y /
        max(image_height, 1)
    )

    ratio = max(
        0,
        min(
            1,
            ratio
        )
    )

    return low + (
        (high - low) *
        ratio
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


        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        full_text = ocr_image(
            image
        )


        symbol = detect_symbol(
            full_text
        )


        timeframe = detect_timeframe(
            full_text
        )


        # ----------------------------------------------------
        # ECHELLE
        # ----------------------------------------------------

        price_scale = read_price_scale(
            image
        )


        # ----------------------------------------------------
        # CHANDELIERS
        # ----------------------------------------------------

        candles = detect_candles(
            image
        )


        # ----------------------------------------------------
        # STRUCTURE
        # ----------------------------------------------------

        structure = detect_structure(
            candles
        )


        # ----------------------------------------------------
        # SUPPORT / RESISTANCE
        # ----------------------------------------------------

        support_y, resistance_y, levels = (
            detect_support_resistance(
                image,
                candles
            )
        )


        # ----------------------------------------------------
        # BREAKOUT / REJET
        # ----------------------------------------------------

        breakout = (
            detect_breakout_rejection(
                candles,
                support_y,
                resistance_y
            )
        )


        # ----------------------------------------------------
        # PRIX
        # ----------------------------------------------------

        entry = None
        support_price = None
        resistance_price = None
        trade = None


        if candles:

            last = candles[-1]

            current_y = (
                last["y"] +
                last["h"] / 2
            )

            # Conversion uniquement si plusieurs
            # prix OCR sont disponibles.

            entry = convert_pixel_to_price(
                current_y,
                height,
                price_scale
            )


            if support_y is not None:

                support_price = (
                    convert_pixel_to_price(
                        support_y,
                        height,
                        price_scale
                    )
                )


            if resistance_y is not None:

                resistance_price = (
                    convert_pixel_to_price(
                        resistance_y,
                        height,
                        price_scale
                    )
                )


        # ----------------------------------------------------
        # TRADE
        # ----------------------------------------------------

        direction = structure[
            "direction"
        ]


        if (
            entry is not None
            and
            (
                support_price is not None
                or
                resistance_price is not None
            )
        ):

            trade = calculate_trade_levels(
                entry,
                support_price,
                resistance_price,
                "BUY"
                if direction == "HAUSSIÈRE"
                else "SELL"
                if direction == "BAISSIÈRE"
                else "NEUTRE"
            )


        # ----------------------------------------------------
        # AFFICHAGE SUPPORT / RESISTANCE
        # ----------------------------------------------------

        support_display = (
            format_price(
                support_price
            )
            if support_price is not None
            else "Non déterminé"
        )


        resistance_display = (
            format_price(
                resistance_price
            )
            if resistance_price is not None
            else "Non déterminée"
        )


        # ----------------------------------------------------
        # TRADE DISPLAY
        # ----------------------------------------------------

        if trade:

            entry_display = format_price(
                trade["entry"]
            )

            sl_display = format_price(
                trade["sl"]
            )

            tp1_display = format_price(
                trade["tp1"]
            )

            tp2_display = format_price(
                trade["tp2"]
            )

            tp3_display = format_price(
                trade["tp3"]
            )

            rr_display = (
                "TP1 1:1 | "
                "TP2 1:2 | "
                "TP3 1:3"
            )

            trade_status = (
                "✅ Prix suffisamment détectés "
                "pour proposer un scénario."
            )

        else:

            entry_display = "Non calculée"
            sl_display = "Non calculé"
            tp1_display = "Non calculé"
            tp2_display = "Non calculé"
            tp3_display = "Non calculé"

            rr_display = "Non calculable"

            trade_status = (
                "⚠️ Prix insuffisamment fiables "
                "pour calculer SL/TP."
            )


        # ----------------------------------------------------
        # CONFIANCE
        # ----------------------------------------------------

        candle_score = min(
            20,
            len(candles)
        )

        level_score = min(
            20,
            len(levels) * 2
        )

        structure_score = 25

        confidence = (
            35 +
            candle_score +
            level_score +
            structure_score
        )

        confidence = min(
            confidence,
            85
        )


        # ----------------------------------------------------
        # RESULTAT
        # ----------------------------------------------------

        analyse = f"""
📊 ANALYSE TRADING AI PRO

━━━━━━━━━━━━━━━━━━

💹 MARCHÉ

Symbole :
{symbol}

Timeframe :
{timeframe}


🕯️ CHANDELIERS

Éléments détectés :
{len(candles)}


📈 STRUCTURE

{structure["structure"]}

Direction :
{structure["direction"]}


🎯 SIGNAL

{structure["signal"]}


🟦 SUPPORT

{support_display}


🟥 RÉSISTANCE

{resistance_display}


🔥 BREAKOUT / REJET

{breakout}


📊 NIVEAUX VISUELS

{len(levels)} niveau(x) détecté(s)


💰 PRIX

Échelle OCR :
{len(price_scale)} valeur(s) détectée(s)


Entrée :
{entry_display}


🛑 STOP LOSS

{sl_display}


✅ TAKE PROFIT

TP1 : {tp1_display}

TP2 : {tp2_display}

TP3 : {tp3_display}


📐 RISK / REWARD

{rr_display}


📊 CONFIANCE STRUCTURELLE

{confidence}%


{trade_status}


⚠️ IMPORTANT

Cette analyse est basée uniquement
sur la capture envoyée.

Si le symbole, le timeframe ou
l'échelle de prix sont mal lus,
le scénario peut être incorrect.

Ne prends pas une position uniquement
sur ce signal.
"""


        return format_analyse(
            analyse
        )


    except Exception as e:

        return (
            "❌ Erreur moteur analyse :\n"
            f"{type(e).__name__}\n"
            f"{str(e)}"
        )

# ============================================================
# TRADING ENGINE
# ============================================================

def format_price(value):
    if value is None:
        return "Non disponible"

    if abs(value) >= 1000:
        return f"{value:.2f}"

    if abs(value) >= 100:
        return f"{value:.2f}"

    if abs(value) >= 10:
        return f"{value:.3f}"

    return f"{value:.5f}"


def calculate_trade_levels(
    entry,
    support,
    resistance,
    direction
):
    """
    Calcule SL / TP uniquement lorsque le prix réel
    et des niveaux cohérents ont été détectés.
    """

    if entry is None:
        return None

    if direction == "BUY":

        # SL sous le support
        if support is not None and support < entry:
            risk = entry - support
            sl = support - (risk * 0.10)
        else:
            return None

        risk = entry - sl

        if risk <= 0:
            return None

        tp1 = entry + risk
        tp2 = entry + (risk * 2)
        tp3 = entry + (risk * 3)

    elif direction == "SELL":

        # SL au-dessus de la résistance
        if resistance is not None and resistance > entry:
            risk = resistance - entry
            sl = resistance + (risk * 0.10)
        else:
            return None

        risk = sl - entry

        if risk <= 0:
            return None

        tp1 = entry - risk
        tp2 = entry - (risk * 2)
        tp3 = entry - (risk * 3)

    else:
        return None

    return {
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "rr1": 1.0,
        "rr2": 2.0,
        "rr3": 3.0
    }


def format_analyse(analyse):
    return f"""
🤖 Trading AI Bot PRO

{analyse}

━━━━━━━━━━━━━━
⚠️ Analyse automatique.
Le marché peut changer rapidement.
Toujours confirmer avant une entrée.
"""

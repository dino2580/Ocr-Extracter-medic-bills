import re

# ------------------------------------------------------------
# 1. OCR DIGIT FIXER
# ------------------------------------------------------------

def fix_ocr_digits(raw: str):
    if raw is None:
        return None

    replacements = {
        "O": "0",
        "o": "0",
        "I": "1",
        "l": "1",
        "S": "5",
        "B": "8",
        " ": "",
    }

    fixed = ""
    changes = 0

    for ch in raw:
        if ch in replacements:
            fixed += replacements[ch]
            changes += 1
        else:
            fixed += ch

    return fixed, changes


# ------------------------------------------------------------
# 2. NUMERIC PARSER
# ------------------------------------------------------------

def parse_number(raw: str):
    """
    Takes raw OCR string and converts to clean float.
    Handles:
        - commas
        - percentages
        - stray characters
    """

    if raw is None:
        return None

    is_percent = "%" in raw

    # Remove everything except digits . , %
    cleaned = re.sub(r"[^0-9.%,-]", "", raw)

    # Remove commas inside number
    cleaned = cleaned.replace(",", "")

    if cleaned.count(".") > 1:
        # fix OCR weird double dots like "21..00"
        cleaned = cleaned.replace("..", ".")

    try:
        if is_percent:
            value = float(cleaned.replace("%", "")) / 100.0
        else:
            value = float(cleaned)
        return value
    except:
        return None


# ------------------------------------------------------------
# 3. MAIN NORMALIZATION PROCESS
# ------------------------------------------------------------

def normalize_step2(raw_tokens):
    """
    Input: raw_tokens from Step 1.
    Output: normalized numeric values + confidence.
    """

    result = []
    total_changes = 0
    total_items = len(raw_tokens)

    for tok in raw_tokens:
        raw_value = tok["raw"]

        # 1. Fix OCR errors
        fixed, changes = fix_ocr_digits(raw_value)
        total_changes += changes

        # 2. Parse into numeric
        parsed_value = parse_number(fixed)

        if parsed_value is None:
            # skip invalid entries
            continue

        result.append({
            "label": tok["label"],
            "value": parsed_value,
            "source": tok.get("source", ""),
            "keyword": tok.get("keyword"),
            "source_string": tok.get("source_string")
        })

    # Confidence decreases if many OCR corrections happened
    if total_items == 0:
        conf = 0
    else:
        error_ratio = total_changes / total_items
        conf = max(0.1, 1.0 - min(0.8, error_ratio * 0.4))

    return {
        "normalized_amounts": result,
        "normalization_confidence": round(conf, 2)
    }

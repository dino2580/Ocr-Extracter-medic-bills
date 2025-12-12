import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract


# ------------------------------------------------------------
# KEYWORDS
# ------------------------------------------------------------

KEYWORDS = {
    "total_bill": [
        "total amount", "total bill", "bill amount", "grand total", "total"
    ],
    "total_paid": [
        "paid amount", "amount paid", "payment", "paid",
        "received amount", "received", "net amount"
    ],
    "total_due": [
        "due amount", "balance", "outstanding", "pending",
        "to pay", "remaining", "due", "balance amount",
        "remaining amount"
    ],
    "discount": [
        "discount amount", "discount", "disamount", "disc",
        "offer", "rebate", "concession", "dis amount",
        "disc amount", "reduced amount"
    ]
}


# ------------------------------------------------------------
# SNIPPET EXTRACTOR
# ------------------------------------------------------------

def extract_snippet(full_text, start_idx, end_idx, context=15):
    snippet_start = max(0, start_idx - context)
    snippet_end = min(len(full_text), end_idx + context)
    snippet = full_text[snippet_start:snippet_end]
    return snippet.replace("\n", " ").strip()


# ------------------------------------------------------------
# CONTEXTUAL TOKEN EXTRACTION (NO NULL RESULTS)
# ------------------------------------------------------------

def extract_contextual_tokens(text: str):
    results = []
    lower_text = text.lower()
    lines = lower_text.split("\n")
    original_lines = text.split("\n")

    for i, line in enumerate(lines):
        clean_line = re.sub(r"\s+", " ", line).strip()

        for label, synonyms in KEYWORDS.items():
            for syn in synonyms:
                syn_lower = syn.lower()

                if syn_lower not in clean_line:
                    continue

                # ----- SAME LINE EXTRACTION -----
                pattern = rf"{re.escape(syn_lower)}[:\s]*([0-9.,%]+)"
                match = re.search(pattern, clean_line)

                if match:
                    val = match.group(1)
                    global_line_start = lower_text.find(clean_line)
                    snippet = extract_snippet(
                        text,
                        global_line_start + match.start(1),
                        global_line_start + match.end(1)
                    )
                    results.append({
                        "label": label,
                        "raw": val,
                        "keyword": syn,
                        "source_string": snippet,
                        "source": "unknown"
                    })
                    continue

                # ----- NEXT LINE EXTRACTION -----
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if re.match(r"^[0-9.,%]+$", next_line):
                        global_start = lower_text.find(next_line)
                        snippet = extract_snippet(
                            text,
                            global_start,
                            global_start + len(next_line)
                        )
                        results.append({
                            "label": label,
                            "raw": next_line,
                            "keyword": syn,
                            "source_string": snippet,
                            "source": "unknown"
                        })
                        continue

                # ❌ DO NOT ADD ANY ENTRY IF NO NUMBER FOUND (NULL REMOVED)

    return results


# ------------------------------------------------------------
# CURRENCY DETECTION
# ------------------------------------------------------------

def detect_currency(text: str):
    t = text.lower()
    if "inr" in t or "₹" in t or "rs" in t:
        return "INR"
    return None


# ------------------------------------------------------------
# OCR PREPROCESS + EXTRACTION
# ------------------------------------------------------------

async def run_ocr(file):
    try:
        file.file.seek(0)
        img = Image.open(file.file)

        img = img.convert("L")
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageEnhance.Contrast(img).enhance(2)
        img = ImageEnhance.Brightness(img).enhance(1.2)

        return pytesseract.image_to_string(img, config="--psm 6")

    except Exception as e:
        print("OCR ERROR:", e)
        return None


# ------------------------------------------------------------
# MERGE LOGIC (LABEL-BASED)
# ------------------------------------------------------------

def merge_tokens(text_tokens, ocr_tokens):
    grouped = {}
    final = []

    # group by label
    for t in text_tokens:
        grouped.setdefault(t["label"], {"text": [], "ocr": []})
        grouped[t["label"]]["text"].append(t)

    for o in ocr_tokens:
        grouped.setdefault(o["label"], {"text": [], "ocr": []})
        grouped[o["label"]]["ocr"].append(o)

    # merge logic
    for label, group in grouped.items():
        text_vals = group["text"]
        ocr_vals = group["ocr"]

        if text_vals and ocr_vals:
            # compare values
            for t in text_vals:
                matched = False
                for o in ocr_vals:
                    if t["raw"] == o["raw"]:
                        merged = t.copy()
                        merged["source"] = "both"
                        final.append(merged)
                        matched = True
                        break
                if not matched:
                    t2 = t.copy()
                    t2["source"] = "text"
                    final.append(t2)

            # Add OCR-only differing values
            for o in ocr_vals:
                if not any(o["raw"] == t["raw"] for t in text_vals):
                    o2 = o.copy()
                    o2["source"] = "ocr"
                    final.append(o2)

        elif text_vals:
            for t in text_vals:
                t2 = t.copy()
                t2["source"] = "text"
                final.append(t2)

        elif ocr_vals:
            for o in ocr_vals:
                o2 = o.copy()
                o2["source"] = "ocr"
                final.append(o2)

    return final


# ------------------------------------------------------------
# MAIN STEP-1 PROCESS
# ------------------------------------------------------------

async def step1_process(file, raw_text):

    text_tokens = []
    ocr_tokens = []
    text_data = ""
    ocr_data = ""

    # OCR first
    if file:
        ocr_data = await run_ocr(file)
        if ocr_data:
            ocr_tokens = extract_contextual_tokens(ocr_data)

    # Text second
    if raw_text:
        text_data = raw_text
        text_tokens = extract_contextual_tokens(raw_text)

    if not text_data and not ocr_data:
        return {"status": "invalid_input", "reason": "No input"}

    merged = merge_tokens(text_tokens, ocr_tokens)

    if not merged:
        return {"status": "no_amounts_found", "reason": "No numeric values found"}

    # confidence
    base_conf = 0.3 + len(merged) * 0.15
    if any(tok["source"] == "ocr" for tok in merged):
        base_conf -= 0.1

    confidence = max(0.1, min(1.0, base_conf))

    # sources used
    sources_used = set()
    for tok in merged:
        if tok["source"] == "both":
            sources_used.update(["text", "ocr"])
        else:
            sources_used.add(tok["source"])

    return {
        "raw_tokens": merged,
        "currency_hint": detect_currency(text_data + " " + ocr_data),
        "confidence": round(confidence, 2),
        "sources_used": sorted(list(sources_used))
    }

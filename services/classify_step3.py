def classify_step3(normalized_output):
    """
    Input:
        normalized_amounts: list of {label, value}
    Output:
        amounts: [
            {"type": "...", "value": ...},
            {"type": "discount", "raw_value": ..., "discount_value": ..., "discount_percent": ...}
        ]
        confidence: float
    """

    amounts = normalized_output.get("normalized_amounts", [])
    classified = {}

    discount_raw = None  # store discount as raw numeric value

    # ------------------------------------------------------------
    # 1. Direct value extraction from Step 2
    # ------------------------------------------------------------
    for item in amounts:
        lbl = item["label"]
        val = item["value"]

        # Handle discount separately
        if lbl == "discount":
            discount_raw = val
            continue

        # Only store first occurrence unless special rules apply
        if lbl not in classified:
            classified[lbl] = val
        else:
            # If multiple values appear — choose the most reliable
            if lbl == "total_bill":
                classified[lbl] = max(classified[lbl], val)
            elif lbl == "total_due":
                classified[lbl] = min(classified[lbl], val)
            elif lbl == "total_paid":
                classified[lbl] = max(classified[lbl], val)

    # ------------------------------------------------------------
    # 2. Compute missing dependent values
    # ------------------------------------------------------------
    total_bill = classified.get("total_bill")
    total_paid = classified.get("total_paid")
    total_due = classified.get("total_due")

    # Compute total_due if missing
    if total_bill is not None and total_paid is not None and total_due is None:
        derived_due = total_bill - total_paid
        if derived_due >= 0:
            classified["total_due"] = derived_due

    # Compute total_paid if missing
    if total_bill is not None and total_due is not None and total_paid is None:
        derived_paid = total_bill - total_due
        if derived_paid >= 0:
            classified["total_paid"] = derived_paid

    # Compute total_bill if missing
    if total_bill is None and total_paid is not None and total_due is not None:
        classified["total_bill"] = total_paid + total_due

    # Refresh computed variables
    total_bill = classified.get("total_bill")

    # ------------------------------------------------------------
    # 3. Discount Interpretation
    # ------------------------------------------------------------
    discount_value = None
    discount_percent = None

    if discount_raw is not None:

        # A. discount_raw < 1 → treat as percent (0.1 → 10%)
        if discount_raw < 1:
            discount_percent = round(discount_raw * 100, 2)
            if total_bill:
                discount_value = round((discount_percent / 100) * total_bill, 2)

        # B. discount_raw >= 1 → treat as absolute amount
        else:
            discount_value = round(discount_raw, 2)
            if total_bill:
                discount_percent = round((discount_value / total_bill) * 100, 2)

    # ------------------------------------------------------------
    # 4. Build final response list
    # ------------------------------------------------------------
    final_list = []

    for key, val in classified.items():
        final_list.append({
            "type": key,
            "value": round(val, 2)
        })

    # Add discount entry if present
    if discount_raw is not None:
        final_list.append({
            "type": "discount",
            "raw_value": discount_raw,
            "discount_value": discount_value,
            "discount_percent": discount_percent
        })

    # ------------------------------------------------------------
    # 5. Confidence Score
    # ------------------------------------------------------------
    conf = 0.5
    if classified.get("total_bill") is not None: conf += 0.2
    if classified.get("total_paid") is not None: conf += 0.15
    if classified.get("total_due") is not None: conf += 0.15
    if discount_raw is not None: conf += 0.1

    conf = round(min(conf, 1.0), 2)

    # ------------------------------------------------------------
    # 6. Final return
    # ------------------------------------------------------------
    return {
        "amounts": final_list,
        "confidence": conf
    }

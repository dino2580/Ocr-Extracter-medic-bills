def assemble_final_output(step1_tokens, step2_norm, step3_classified, currency="INR"):
    """
    Step 4: Assemble final result with provenance and discount details.
    """

    final_output_amounts = []

    # ------------------------------------------------------------
    # BUILD PROVENANCE LOOKUP TABLE FROM STEP 1
    # ------------------------------------------------------------
    provenance_map = {}   # label -> source matched string

    for token in step1_tokens:
        lbl = token["label"]
        src = token.get("source_string", "")

        # Keep first seen source only (most reliable)
        if lbl not in provenance_map:
            provenance_map[lbl] = src

    # ------------------------------------------------------------
    # PARSE CLASSIFIED OUTPUT FROM STEP 3
    # ------------------------------------------------------------
    for item in step3_classified.get("amounts", []):

        label = item["type"]

        # ----------- 1. Determine numeric value -----------
        if label == "discount":
            # Discount may have multiple numeric meanings
            numeric_value = item.get("discount_value")
            discount_percent = item.get("discount_percent")

            # Extract provenance text
            if "discount" in provenance_map:
                source_text = f"text: '{provenance_map['discount']}'"
            else:
                source_text = "computed"

            # Add discount_value entry if it exists
            if numeric_value is not None:
                final_output_amounts.append({
                    "type": "discount_value",
                    "value": numeric_value,
                    "source": source_text
                })

            # Add percent entry if it exists
            if discount_percent is not None:
                final_output_amounts.append({
                    "type": "discount_percent",
                    "value": discount_percent,
                    "source": source_text
                })

            continue  # skip default handling

        # ----------- 2. Normal case (total_bill, paid, due) -----------
        value = item.get("value")
        if value is None:
            continue  # skip invalid item

        # PROVENANCE for non-discount values
        if label in provenance_map:
            source_text = f"text: '{provenance_map[label]}'"
        else:
            source_text = "computed"

        final_output_amounts.append({
            "type": label,
            "value": value,
            "source": source_text
        })

    # ------------------------------------------------------------
    # FINAL RESPONSE FORMAT
    # ------------------------------------------------------------
    return {
        "currency": currency or "INR",
        "amounts": final_output_amounts,
        "status": "ok"
    }

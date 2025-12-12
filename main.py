from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

# Import step logic modules
from services.ocr_step1 import step1_process
from services.normalize_step2 import normalize_step2
from services.classify_step3 import classify_step3
from services.final_step4 import assemble_final_output

app = FastAPI(title="AI Medical Bill Extractor")


# ------------------------------------------------------------
# STEP 1: OCR / TEXT EXTRACTION (Returns only Step1 output)
# ------------------------------------------------------------
@app.post("/step1/extract")
async def api_step1(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    result = await step1_process(file, text)

    if result.get("status") in ["invalid_input", "no_amounts_found"]:
        return JSONResponse(status_code=422, content=result)

    return result



# ------------------------------------------------------------
# STEP 2: NORMALIZATION (Auto-run Step1, but return ONLY Step2 output)
# ------------------------------------------------------------
@app.post("/step2/normalize")
async def api_step2(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    # Run Step 1
    step1 = await step1_process(file, text)

    if step1.get("status") == "no_amounts_found":
        return JSONResponse(status_code=422, content=step1)

    # Run Step 2
    step2 = normalize_step2(step1["raw_tokens"])

    return step2  # <-- ONLY Step2 result returned



# ------------------------------------------------------------
# STEP 3: CLASSIFICATION (Auto-run Step1 + Step2, return ONLY Step3 output)
# ------------------------------------------------------------
@app.post("/step3/classify")
async def api_step3(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    # Step 1
    step1 = await step1_process(file, text)
    if step1.get("status") == "no_amounts_found":
        return JSONResponse(status_code=422, content=step1)

    # Step 2
    step2 = normalize_step2(step1["raw_tokens"])
    normalized = step2["normalized_amounts"]

    # Step 3
    step3 = classify_step3({"normalized_amounts": normalized})

    return step3  # <-- ONLY Step3 results returned



# ------------------------------------------------------------
# STEP 4: FINAL OUTPUT (Auto-run all steps, return ONLY Step4 output)
# ------------------------------------------------------------
@app.post("/step4/finalize")
async def api_step4(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    # Step 1
    step1 = await step1_process(file, text)
    if step1.get("status") == "no_amounts_found":
        return JSONResponse(status_code=422, content=step1)

    # Step 2
    step2 = normalize_step2(step1["raw_tokens"])
    normalized = step2["normalized_amounts"]

    # Step 3
    step3 = classify_step3({"normalized_amounts": normalized})

    # Step 4
    final = assemble_final_output(
        step1_tokens=step1["raw_tokens"],
        step2_norm=step2,
        step3_classified=step3,
        currency=step1["currency_hint"]
    )

    return final  # <-- ONLY Step4 final output returned

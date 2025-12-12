Activate venv
pip install -r requirements.txt
exceute this command -uvicorn main:app --reload --port 3000
http://localhost:3000/step1/extract
http://localhost:3000/step2/normalize
http://localhost:3000/step3/classify
http://localhost:3000/step4/finalize
Req Type-Post
Input-file-file(for ocr),text-text(already available text)

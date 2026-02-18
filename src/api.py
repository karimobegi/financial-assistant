from fastapi import FastAPI, HTTPException, UploadFile, File
from src.ingest import ingest_transactions
from src.persist import add_rows
from src.analysis import run_analysis
from src.advice import generate_advice
from src.db import db_stats, reset_db
from src.safe_analysis import make_json_safe
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/Website"), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/app")

@app.get("/app")
def app_page():
    return FileResponse("src/Website/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(
    input_path: str = "data/raw_transactions.csv",
    output_path: str = "data/clean_transactions.csv",
):
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Input CSV not found")

    ingest_summary = ingest_transactions(input_path=input_path, output_path=output_path)

    if ingest_summary["rows_read"] == 0:
        raise HTTPException(status_code=400, detail="Input CSV is empty")
    if ingest_summary["rows_written"] == 0:
        raise HTTPException(status_code=400, detail="No valid rows after cleaning")

    return ingest_summary


@app.post("/persist")
def persist(input_path: str = "data/clean_transactions.csv"):
    return add_rows(input_path)


@app.get("/analysis")
def analysis(db_path: str = "data/finance.db"):
    results = run_analysis(db_path)
    return make_json_safe(results)


@app.get("/advice")
def advice(db_path: str = "data/finance.db"):
    results = run_analysis(db_path)
    return {"advice": generate_advice(results)}


@app.get("/db/stats")
def get_db_stats():
    return db_stats()


@app.post("/run-all")
async def run_all(
    file: UploadFile = File(...),
    clean_path: str = "data/clean_transactions.csv",
    db_path: str = "data/finance.db",
    reset: bool = False,
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    if reset:
        reset_db()

    raw_path = UPLOAD_DIR / file.filename
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")

    raw_path.write_bytes(contents)

    ingest_summary = ingest_transactions(
        input_path=str(raw_path),
        output_path=clean_path,
    )
    if ingest_summary["rows_written"] == 0:
        raise HTTPException(status_code=400, detail="No valid rows after cleaning")

    persist_summary = add_rows(clean_path)
    results = run_analysis(db_path)

    return {
        "ingest": ingest_summary,
        "persist": persist_summary,
        "analysis": make_json_safe(results),
        "advice": generate_advice(results),
        "raw_saved_as": str(raw_path),
    }
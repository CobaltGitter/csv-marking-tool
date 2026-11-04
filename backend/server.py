# backend/server.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd, io
from backend.marker_core import mark_wide_df  # import your logic wrapper

app = FastAPI()

# If I run the front-end on a different port (e.g. 5500), enable CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://127.0.0.1:5500',
        'http://localhost:5500',
    ],           
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/ping')
def ping():
    return {'status':'pong'}

@app.post("/mark")
async def mark(
    file: UploadFile,
    number_mode: str = Form("relative"),
    tolerance: float = Form(0.001),
    spell_threshold: int = Form(80),
    list_order: str = Form("ignore"),      # "ignore" | "enforce"
    list_delim: str = Form(""),
):
    content = await file.read()
    df_in = pd.read_csv(io.BytesIO(content))
    df_out = mark_wide_df(
        df_in.copy(),
        number_mode=number_mode,
        tol=float(tolerance),
        spell_threshold=int(spell_threshold),
        list_order_matters=(list_order == "enforce"),
        list_delim=list_delim.strip()
    )
    buf = io.StringIO()
    df_out.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv")

from pathlib import Path
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
import io

from backend.marker_core import mark_wide_df

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

app.mount("/dist", StaticFiles(directory=str(DIST_DIR)), name="dist")

@app.get("/")
def read_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/ping")
def ping():
    return {"status": "pong"}

@app.post("/mark")
async def mark(
    file: UploadFile = File(...),
    number_mode: str = Form("relative"),
    tolerance: float = Form(0.001),
    spell_threshold: int = Form(80),
    list_order: str = Form("ignore"),
    list_delim: str = Form(""),
):
    content = await file.read()
    df_in = pd.read_csv(io.BytesIO(content))
    df_out = mark_wide_df(
        df_in.copy(),
        number_mode=number_mode,
        tol=float(tolerance),
        spell_threshold=int(spell_threshold),
        list_order_matters=(list_order == "enforce"),
        list_delim=list_delim.strip(),
    )
    buf = io.StringIO()
    df_out.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv")

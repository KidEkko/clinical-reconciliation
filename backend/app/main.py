from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.reconcile import router as reconcile_router
from app.api.routes.data_quality import router as data_quality_router

app = FastAPI(title="Clinical Data Reconciliation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(reconcile_router)
app.include_router(data_quality_router)
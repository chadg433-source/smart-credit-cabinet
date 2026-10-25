from fastapi import FastAPI
from app.api.applications import router as applications_router
from app.api.products import router as products_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Smart Credit Cabinet")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)
app.include_router(products_router)
@app.get("/health")
def health():
    return {"status": "ok"}
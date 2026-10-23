from fastapi import FastAPI
from app.api.applications import router as applications_router
from app.api.products import router as products_router
app = FastAPI(title="Smart Credit Cabinet")

app.include_router(applications_router)
app.include_router(products_router)
@app.get("/health")
def health():
    return {"status": "ok"}
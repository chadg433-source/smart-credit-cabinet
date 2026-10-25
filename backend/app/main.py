from fastapi import FastAPI
from app.api.applications import router as applications_router
from app.api.products import router as products_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Smart Credit Cabinet")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешаем всем (для хакатона безопасно)
    allow_credentials=False, # Если стоит True с "*", будет ошибка
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)
app.include_router(products_router)
@app.get("/health")
def health():
    return {"status": "ok"}
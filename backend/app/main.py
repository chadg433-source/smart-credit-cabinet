from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.applications import router as applications_router
from app.api.products import router as products_router
from app.api.authorization import router as authorization_router
from app.api.businesses import router as businesses_router


app = FastAPI(title="Smart Credit Cabinet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)
app.include_router(products_router)
app.include_router(authorization_router)
app.include_router(businesses_router)


@app.get("/health")
def health():
    return {"status": "ok"}

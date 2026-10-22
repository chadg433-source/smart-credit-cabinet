from fastapi import FastAPI

app = FastAPI(title="Smart Credit Cabinet")

@app.get("/health")
def health():
    return {"status": "ok"}
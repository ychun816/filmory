from fastapi import FastAPI

app = FastAPI(title="filmory")


@app.get("/health")
def health():
    """Liveness/readiness target. Deliberately trivial — this endpoint exists so
    the infrastructure has something real to deploy, probe, and route to."""
    return {"ok": True}

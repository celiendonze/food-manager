"""FastAPI app root."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello from the Food Manager API!"}

from fastapi import FastAPI


app = FastAPI(
    title="Student AI API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Student AI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
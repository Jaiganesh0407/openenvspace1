from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server running"}

@app.post("/reset")
def reset():
    return {"status": "ok"}

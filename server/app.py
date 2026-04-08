from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    return {"observation": {}, "reward": 0.0, "done": False, "info": {}}

@app.post("/step")
def step():
    return {"observation": {}, "reward": 1.0, "done": True, "info": {}}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()

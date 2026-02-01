from fastapi import FastAPI

app = FastAPI(title="Aura Backend")

@app.get("/")
def home():
    return {"message": "Aura Backend Running!"}

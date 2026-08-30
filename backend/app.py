from fastapi import FastAPI

# Инициализация fastapi
app = FastAPI()


# Роуты
@app.get("/health")
def healthChecker():
  return {"message": "All rights!"}

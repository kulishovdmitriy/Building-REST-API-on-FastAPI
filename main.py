import fastapi
import uvicorn

app = fastapi.FastAPI()


@app.get("/")
def index():
    return {"message": "Hello world"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True
    )

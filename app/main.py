import fastapi
import uvicorn
from app.routers import router

if __name__ == "__main__":
    app = fastapi.FastAPI()
    app.include_router(router)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
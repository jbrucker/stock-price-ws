import fastapi
import uvicorn
from app.routers import router

if __name__ == "__main__":
    app1 = fastapi.FastAPI()
    app1.include_router(router)
    
    uvicorn.run(app1, host="127.0.0.1", port=8000)
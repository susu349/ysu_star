from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .core.config import get_settings
from .core.database import engine, Base
from .api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        from .core.milvus import get_milvus_client
        milvus_client = get_milvus_client()
        milvus_client.connect()
    except Exception as e:
        print(f"⚠️ Milvus连接失败（可选组件）: {e}")
        print("   用户认证模块仍然可以正常使用")
    yield
    try:
        from .core.milvus import get_milvus_client
        milvus_client = get_milvus_client()
        milvus_client.disconnect()
    except:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="校园AI助手后端API",
    lifespan=lifespan,
    debug=settings.is_dev,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载地图瓦片静态文件服务
TILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "map_tiles")
os.makedirs(TILES_DIR, exist_ok=True)
app.mount("/map-tiles", StaticFiles(directory=TILES_DIR), name="map_tiles")

# 挂载上传文件服务
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app_name": settings.APP_NAME}


@app.get("/")
def root():
    return {
        "message": "欢迎使用校园AI助手",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "campus_ai.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.is_dev,
    )

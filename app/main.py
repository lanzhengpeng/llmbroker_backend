# main.py
from fastapi import FastAPI
from api.chat import router as chat_router
from api.monitor import  router as monitor_router
# 创建 FastAPI 实例
app = FastAPI(title="LLM Broker Backend", version="1.0")

# 只注册路由
app.include_router(chat_router)
app.include_router(monitor_router)
# 启动 Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,
        reload=True,     # 开发模式自动重载
        log_level="info" # 显示访问日志
    )

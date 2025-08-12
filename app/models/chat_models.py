from pydantic import BaseModel

class ChatRequest(BaseModel):
    model: str = "GLM-4.5-Flash"  # 给个默认值，也可以请求时指定
    message: str

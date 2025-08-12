from fastapi import APIRouter
import os
from models.chat_models import ChatRequest
from entension.my_openai import MyOpenAI as OpenAI
from fastapi.responses import StreamingResponse
router = APIRouter()

SERVER_IP = os.environ.get("SERVER_IP", "")
client = OpenAI(
    api_key=os.environ.get("PASSWORD", ""),
    base_url=f"http://{SERVER_IP}:8000/v1"
)

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = client.chat.completions.create(
        model=request.model,
        messages=[{
            "role": "system",
            "content": "你是一个聪明且富有创造力的小说作家"
        }, {
            "role": "user",
            "content": request.message
        }],
        top_p=0.7,
        temperature=0.9,
        stream=False  # 关闭流式
    )
    content = response.choices[0].message.content
    return {"reply": content}

@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    def event_generator():
        stream = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": "你是一个聪明且富有创造力的小说作家"},
                {"role": "user", "content": request.message}
            ],
            top_p=0.7,
            temperature=0.9,
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")
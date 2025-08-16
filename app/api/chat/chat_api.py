from fastapi import APIRouter
import os
from api.chat.models.chat_models import ChatRequest
from entension.my_openai import MyOpenAI as OpenAI
from fastapi.responses import StreamingResponse
from fastapi import Request
from api.chat.chatbot.chatbot import ChatBot
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

def event_generator(model: str, message: str):
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个聪明且富有创造力的小说作家"},
            {"role": "user", "content": message}
        ],
        top_p=0.7,
        temperature=0.9,
        stream=True
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content

chatbot=ChatBot(client=client, system_prompt="你是一个聪明且富有创造力的小说作家")
@router.post("/chat/stream")
async def chat_stream_endpoint(request: Request, chat_request: ChatRequest):
    user_ip = request.client.host  # 获取客户端IP，做用户唯一标识

    # 调用 ChatBot 的 chat_stream 生成器，传入用户 IP 和请求参数
    generator = chatbot.chat_stream(user_id=user_ip,
                                    user_message=chat_request.message,
                                    model=chat_request.model,
                                    temperature=0.9,
                                    top_p=0.7)

    return StreamingResponse(generator, media_type="text/plain; charset=utf-8")



from api.chat.chatbot.multi_tool_agent import check_answer_direct, select_tool, fill_tool_params  
# 导入多工具智能问答流程相关函数：
# check_answer_direct: 判断问题是否可直接回答
# select_tool: 从工具列表中选择最合适的工具
# fill_tool_params: 根据问题生成工具调用参数

from api.mcp.mcp_tools.tools import get_tools_dict, get_tool_details, load_tool_from_db  
# 导入工具数据库操作相关函数：
# get_tools_dict: 获取工具名称->描述字典
# get_tool_details: 获取工具的 modifiable_fields 和 usage_example
# load_tool_from_db: 从数据库加载工具信息

from api.mcp.mcp_tools.register_tool import tools  
# 导入已注册工具字典 tools，包含工具函数及信息

from api.prompts.mcp_prompts import FINAL_ANSWER  
# 导入最终回答提示词模板

import json  # 用于 JSON 字符串和对象之间转换

@router.post("/chat/mcp/stream")  
# FastAPI 路由，POST 请求，路径为 /chat/mcp/stream
async def chat_mcp_stream_generator(chat_request: ChatRequest):  
    # 异步函数处理前端请求，参数 chat_request 是用户消息和模型信息

    is_useTool = check_answer_direct(client, chat_request.model, chat_request.message)  
    # 步骤1：判断问题是否需要使用工具，返回 "直接回答" 或 "需要工具"

    if is_useTool == "需要工具":  
        # 如果问题需要使用工具

        tools_dict = get_tools_dict()  
        # 获取数据库中所有工具的字典：{工具名: 描述}

        tool_name = select_tool(client, chat_request.model, chat_request.message, tools_dict)  
        # 步骤2：选择最合适的工具，返回工具名称

        details = get_tool_details(tool_name)  
        # 查询该工具的 modifiable_fields 和 usage_example

        tool_params = fill_tool_params(client, chat_request.model, chat_request.message, tool_name, tools_dict[tool_name], details)  
        # 步骤3：生成工具调用参数，返回 JSON 字符串

        obj = json.loads(tool_params)  
        # 将 JSON 字符串转换为 Python 字典，方便传给工具函数

        load_tool_from_db(tool_name)  
        # 从数据库加载工具信息（可选，可初始化工具环境或缓存）
        global tools
        tool_result = tools[tool_name]["func"](params=obj)  
        # 调用注册工具的函数，传入生成的参数，得到工具返回结果
        # 用完之后删除当前工具
        del tools[tool_name]
        async def generator():  # 生成器函数，用于流式返回
            final_answer = FINAL_ANSWER.format(question=chat_request.message, tool_result=tool_result)  
            # 用模板生成最终回答，把工具返回结果嵌入回答

            stream = client.chat.completions.create(
                model=chat_request.model,  # 使用用户指定模型
                messages=[{
                    "role": "system",
                    "content": "你是一个有用的助手"  # 系统角色设定
                }, {
                    "role": "user",
                    "content": final_answer  # 用户消息为最终回答内容
                }],
                top_p=0.7,
                temperature=0.9,
                stream=True  # 开启流式输出
            )

            for chunk in stream:  
                # 遍历流式输出的每个片段
                content = chunk.choices[0].delta.content  
                # 获取本次片段的文本内容
                if content is not None:  
                    yield content  # 原模原样输出给前端

    else:  
        # 如果问题可以直接回答，不需要工具

        async def generator():  # 生成器函数
            stream = client.chat.completions.create(
                model=chat_request.model,  # 使用用户指定模型
                messages=[{
                    "role": "system",
                    "content": "你是一个有用的助手"
                }, {
                    "role": "user",
                    "content": chat_request.message  # 直接使用用户原问题
                }],
                top_p=0.7,
                temperature=0.9,
                stream=True  # 开启流式输出
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content  # 原模原样输出给前端

    return StreamingResponse(generator(), media_type="text/plain; charset=utf-8")  
    # 返回 StreamingResponse，流式返回生成器的内容，类型为纯文本


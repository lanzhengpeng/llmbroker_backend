from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Optional, Any
from api.mcp.mcp_tools.register_tool import parse_curl_and_register # , tools
from api.mcp.mcp_tools.tools import load_tool_from_db,save_tool_to_db,get_tools_dict
from api.mcp.mcp_tools.tools import delete_tool_by_name  # 导入你写的删除函数
router = APIRouter()

from typing import Optional, Dict, Any

class ToolRegister(BaseModel):
    curl: str
    name: str
    description: Optional[str] = None            # 工具描述
    auth_required: Optional[bool] = True         # 是否需要认证
    modifiable_fields: Optional[Dict[str, Any]] = {}  # 可修改参数
    usage_example: Optional[Dict[str, Any]] = {}      # 使用示例


class ToolCall(BaseModel):
    params: Optional[Dict[str, Any]] = {}
    token: Optional[str] = None

# 查询工具列表
@router.get("/tools")
def list_tools():
    dict = get_tools_dict()
    return {"tools": dict}
    # return {"tools": list(tools.keys())}

from fastapi import HTTPException

# 注册工具
@router.post("/tools/register")
def register_tool_route(payload: ToolRegister):
    # 调用保存函数并获取返回值
    success = save_tool_to_db(
        name=payload.name,
        description=payload.description,
        curl_cmd=payload.curl,   # 注意 Pydantic 字段名是 curl
        auth_required=payload.auth_required,
        modifiable_fields=getattr(payload, "modifiable_fields", {}),  # 可选字段
        usage_example=getattr(payload, "usage_example", {})           # 可选字段
    )

    if not success:
        msg = f"工具 {payload.name} 注册失败"
        raise HTTPException(status_code=400, detail=msg)
    
    msg = f"工具 {payload.name} 注册成功"
    return {"message": msg}


# 删除工具
@router.delete("/tools/{tool_name}")
def delete_tool_route(tool_name: str):
    """
    根据工具名称删除工具
    """
    

    success = delete_tool_by_name(tool_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"工具 '{tool_name}' 不存在")
    return {"message": f"工具 '{tool_name}' 已删除"}

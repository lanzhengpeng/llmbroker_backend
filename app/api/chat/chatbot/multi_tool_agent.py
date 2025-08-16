from api.prompts.mcp_prompts import QUERY_BOOL, TOOL_SELECT, TOOL_FILL_PARAMS

def check_answer_direct(client, model, request_message):
    """
    步骤 1：判断问题是否可以直接回答
    返回值：query_bool -> "直接回答" 或 "需要工具"
    """
    query_bool_prompt = QUERY_BOOL.format(question=request_message)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个智能问答助手"},
            {"role": "user", "content": query_bool_prompt}
        ],
        top_p=0.7,
        temperature=0.9,
        stream=False
    )
    query_bool = response.choices[0].message.content.strip()
    return query_bool


def select_tool(client, model, request_message, tools_dict):
    """
    步骤 2：从工具字典中选择最合适的工具
    参数：
        tools_dict: dict，key 是工具名称，value 是工具描述
    返回值：
        selected_tool -> 工具名称，或 "无可用工具"
    """
    # 将字典转换成 prompt 文本
    tools_text = "\n".join([f"{name}：{desc}" for name, desc in tools_dict.items()])
    
    tool_select_prompt = TOOL_SELECT.format(question=request_message, tools_list=tools_text)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个智能问答助手"},
            {"role": "user", "content": tool_select_prompt}
        ],
        top_p=0.7,
        temperature=0.9,
        stream=False
    )
    
    selected_tool = response.choices[0].message.content.strip()
    return selected_tool



def fill_tool_params(client, model, request_message, selected_tool, tool_desc, params_example):
    """
    步骤 3：根据工具描述和用户问题生成完整参数
    返回值：tool_params -> JSON 字符串
    """
    fill_prompt = TOOL_FILL_PARAMS.format(
        question=request_message,
        tool_name=selected_tool,
        tool_desc=tool_desc,
        params_example=params_example
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个智能问答助手"},
            {"role": "user", "content": fill_prompt}
        ],
        top_p=0.7,
        temperature=0.9,
        stream=False
    )
    tool_params = response.choices[0].message.content.strip()
    return tool_params

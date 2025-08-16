import requests  # 用于发送 HTTP 请求
import re        # 正则表达式，用于解析 curl 命令
import json      # 用于处理 JSON 数据
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse  # URL 解析和拼接

tools = {}  # 全局字典，用来存储注册的工具函数

# 注册工具函数到全局字典
def register_tool(name, func, auth_required=True):
    # key: 工具名称, value: 字典包含函数对象和是否需要授权
    tools[name] = {"func": func, "auth_required": auth_required}

# 递归合并字典，用于 POST 请求中合并参数
def deep_update(orig: dict, updates: dict):
    for k, v in updates.items():
        # 如果原字典和更新字典对应 key 的值都是字典，则递归合并
        if k in orig and isinstance(orig[k], dict) and isinstance(v, dict):
            deep_update(orig[k], v)
        else:
            # 否则直接覆盖原字典的值
            orig[k] = v
    return orig  # 返回合并后的字典

# 解析 curl 命令并注册为工具函数
def parse_curl_and_register(curl_text: str, tool_name: str, auth_required: bool = True):
    try:
        # 使用正则提取 curl 命令中的 URL
        url_match = re.search(r'curl .*?"(http.*?)"', curl_text)
        if not url_match:
            raise ValueError("无法解析 URL")
        url = url_match.group(1)  # 提取到 URL 字符串

        # 判断请求方法，默认 GET
        method = "GET"
        # 如果 curl 命令包含 POST 或 -d 表示有数据，则改为 POST
        if "-X POST" in curl_text or " -d " in curl_text:
            method = "POST"

        # 提取 headers，格式为字典
        headers = {}
        for h in re.findall(r'-H\s+"(.*?):\s*(.*?)"', curl_text):
            k, v = h
            headers[k.strip()] = v.strip()

        # 提取 POST 数据
        data_match = re.search(r"-d\s+'(.*?)'", curl_text)
        raw_data = data_match.group(1) if data_match else None  # 原始数据字符串

        # 如果数据是 JSON，尝试解析成字典
        try:
            orig_body = json.loads(raw_data) if raw_data else {}
        except:
            orig_body = raw_data  # 如果不是 JSON，保留原始字符串

        # 封装工具函数
        def tool_func(params=None, token=None):
            req_headers = headers.copy()  # 拷贝 headers，防止修改原字典
            if token:
                req_headers["Authorization"] = token  # 添加 token 到请求头

            if method == "GET":
                # 处理 GET 请求
                parsed = urlparse(url)  # 解析 URL
                query = parse_qs(parsed.query)  # 解析原始 query 参数
                if params:
                    # 如果传了参数，覆盖或添加到 query
                    for k, v in params.items():
                        query[k] = [v] if not isinstance(v, list) else v
                # 拼接最终 URL
                final_url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
                return requests.get(final_url, headers=req_headers).json()  # 发起 GET 请求并返回 JSON

            else:
                # 处理 POST 请求
                if isinstance(orig_body, dict):
                    # 如果原始 body 是 JSON，复制一份
                    body = orig_body.copy()
                    if params:
                        deep_update(body, params)  # 使用递归合并参数
                    return requests.post(url, headers=req_headers, json=body).json()  # POST JSON
                else:
                    # 如果 body 是字符串，直接使用
                    body = params if params else orig_body
                    return requests.post(url, headers=req_headers, data=body).json()  # POST 普通数据

        # 注册工具函数到全局字典
        register_tool(tool_name, tool_func, auth_required)
        print(f"[REGISTER] Tool '{tool_name}' registered successfully!")  # 打印注册成功信息

    except Exception as e:
        # 捕获异常并打印
        print(f"[ERROR] Failed to register tool '{tool_name}': {e}")
        raise  # 抛出异常

import sqlite3
import json
import os
from typing import Dict
from api.mcp.mcp_tools.register_tool import parse_curl_and_register, tools
def load_tool_from_db(name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "../../../config/mcpTools.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT curl_cmd, auth_required, modifiable_fields, usage_example
        FROM tools WHERE name=?
    """, (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"Tool {name} not found in DB")

    curl_cmd, auth_required, modifiable_fields, usage_example = row
    modifiable_fields = json.loads(modifiable_fields)
    usage_example = json.loads(usage_example)

    # 注册成函数
    parse_curl_and_register(curl_cmd, name, bool(auth_required))

    return {
        "func": tools[name]["func"],
        "fields": modifiable_fields,
        "example": usage_example
    }



def save_tool_to_db(name, description, curl_cmd, auth_required,
                    modifiable_fields, usage_example) -> bool:
    """
    保存工具信息到数据库，如果已有同名工具则替换。

    返回：
        bool: True 表示成功，False 表示失败
    """
    try:
        # 当前脚本所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "../../../config/mcpTools.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO tools (name, description, curl_cmd, auth_required, modifiable_fields, usage_example)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, description, curl_cmd, int(auth_required),
             json.dumps(modifiable_fields, ensure_ascii=False),
             json.dumps(usage_example, ensure_ascii=False))
        )

        conn.commit()
        return True
    except Exception as e:
        print("保存工具失败:", e)
        return False
    finally:
        conn.close()


def get_tools_dict() -> Dict[str, str]:
    """
    从 SQLite 数据库中查询 tools 表，返回 {name: description} 字典
    
    返回：
        Dict[str, str]：key 是工具名称，value 是工具描述
    """
    # 当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "../../../config/mcpTools.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name, description FROM tools")
        rows = cursor.fetchall()
        tools_dict = {name: desc for name, desc in rows}
    finally:
        cursor.close()
        conn.close()

    return tools_dict
import os
import sqlite3
import json
from typing import Dict, Any


def get_tool_details(tool_name: str) -> Dict[str, Any]:
    """
    根据工具名称查询数据库，获取 modifiable_fields 和 usage_example
    
    参数：
        tool_name: 工具名称
    
    返回：
        Dict[str, Any]，包含：
            - "modifiable_fields": dict
            - "usage_example": dict
    """
    # 当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "../../../config/mcpTools.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT modifiable_fields, usage_example FROM tools WHERE name=?",
            (tool_name, ))
        row = cursor.fetchone()
        if row:
            # modifiable_fields 是 JSON 字符串
            modifiable_fields = json.loads(row[0]) if row[0] else {}
            # usage_example 假设存储为 JSON 字符串
            usage_example = json.loads(row[1]) if row[1] else {}
            return {
                "modifiable_fields": modifiable_fields,
                "usage_example": usage_example
            }
        else:
            return {"modifiable_fields": {}, "usage_example": {}}
    finally:
        cursor.close()
        conn.close()

import sqlite3

def delete_tool_by_name(tool_name: str) -> bool:
    """
    根据工具名称从数据库删除工具

    参数：
        tool_name: str，工具名称

    返回：
        bool: True 表示删除成功，False 表示工具不存在
    """
    # 当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "../../../config/mcpTools.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM tools WHERE name=?", (tool_name,))
        count = cursor.fetchone()[0]
        if count == 0:
            return False  # 工具不存在
        
        cursor.execute("DELETE FROM tools WHERE name=?", (tool_name,))
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


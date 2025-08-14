from typing import Dict, List
from threading import Lock

class ChatBot:
    def __init__(self, client, system_prompt: str):
        self.client = client
        self.system_prompt = system_prompt
        self.histories: Dict[str, List[dict]] = {}
        self.lock = Lock()  # 简单线程安全锁
    
    def _init_history(self, user_id: str):
        # 初始化用户历史
        self.histories[user_id] = [{"role": "system", "content": self.system_prompt}]
    
    def clear_history(self, user_id: str):
        with self.lock:
            self._init_history(user_id)
    
    def chat_stream(self, user_id: str, user_message: str, model: str, temperature=0.9, top_p=0.7):
        with self.lock:
            if user_id not in self.histories:
                self._init_history(user_id)
            history = self.histories[user_id]
            
            # 添加用户输入
            history.append({"role": "user", "content": user_message})
        
        assistant_response = ""
        
        # 调用模型接口，传递上下文历史
        stream = self.client.chat.completions.create(
            model=model,
            messages=history,
            temperature=temperature,
            top_p=top_p,
            stream=True
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                assistant_response += content
                yield content
        
        # 结束后把AI回答追加到历史
        with self.lock:
            history.append({"role": "assistant", "content": assistant_response})
            self.histories[user_id] = history
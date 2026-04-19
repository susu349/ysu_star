"""
LLM客户端 - 支持DeepSeek等大模型
"""
import json
from typing import Optional, Dict, Any, List
from httpx import Client, Timeout
from ..config import get_settings

settings = get_settings()


class LLMClient:
    """大模型客户端"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL
        self.model = model or settings.LLM_MODEL
        self.timeout = Timeout(timeout=120.0)
        self.client = Client(timeout=self.timeout)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Optional[str]:
        """聊天接口"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return None

    def chat_with_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> Optional[Dict[str, Any]]:
        """返回JSON格式的响应"""
        # 添加强制JSON输出的提示
        system_prompt = {
            "role": "system",
            "content": "你是一个专业的数据提取助手。请严格按照JSON格式输出，不要包含任何Markdown标记或额外文本。"
        }

        if messages and messages[0]["role"] == "system":
            messages[0] = system_prompt
        else:
            messages.insert(0, system_prompt)

        response = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        if not response:
            return None

        # 尝试解析JSON
        try:
            # 清理响应（有时候LLM会在JSON外加点东西）
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始响应: {response}")
            return None

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_llm_client() -> LLMClient:
    """获取LLM客户端实例"""
    return LLMClient()

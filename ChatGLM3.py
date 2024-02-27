import logging
from typing import Any, List, Mapping, Optional

import requests
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import LLMResult
from langchain_community.llms.utils import enforce_stop_tokens

logger = logging.getLogger(__name__)

# 定义一个名为 ChatGLM3 的语言模型类，继承自 LLM 类
class ChatGLM3(LLM):
    # 定义端点 URL，模型参数等属性
    endpoint_url: str = "http://127.0.0.1:8000/"
    model_kwargs: Optional[dict] = None
    max_token: int = 800000
    temperature: float = 0.1
    history: List[List] = []
    top_p: float = 0.9
    with_history: bool = False

    @property
    def _llm_type(self) -> str:
        return "chat_glm3"  # 返回语言模型类型字符串表示

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        _model_kwargs = self.model_kwargs or {}
        return {
            **{"endpoint_url": self.endpoint_url},
            **{"model_kwargs": _model_kwargs},
        }

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """Call out to a ChatGLM LLM inference endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.
        """

        _model_kwargs = self.model_kwargs or {}

        # 设置 HTTP 请求头部
        headers = {"Content-Type": "application/json"}

        # 构建会话历史
        chat_messages = [{"role": "user", "content": prompt}]

        # 构建请求数据
        data = {
            "model": "chatglm3",
            "messages": chat_messages,
            "stream": False,
            "max_tokens": 80000,
            "temperature": 0.8,
            "top_p": 0.8,
        }

        # 调用推理端点
        try:
            response = requests.post(f"{self.endpoint_url}v1/chat/completions", headers=headers, json=data, stream=False)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        if response.status_code != 200:
            raise ValueError(f"Failed with response: {response}")

        try:
            parsed_response = response.json()
            text = parsed_response.get("choices", [{}])[0].get("message", "").get("content", "")

        except requests.exceptions.JSONDecodeError as e:  # 处理 JSON 解析错误
            raise ValueError(
                f"Error raised during decoding response from inference endpoint: {e}."
                f"\nResponse: {response.text}"
            )

        if stop is not None:
            text = enforce_stop_tokens(text, stop)  # 处理停止词

        if self.with_history:
            self.history = self.history + [[None, parsed_response["response"]]]  # 将生成的文本追加到历史记录中

        return text  # 返回生成的文本
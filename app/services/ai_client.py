from abc import ABC, abstractmethod
from typing import Dict, Any
import openai
from app.config import get_settings

settings = get_settings()


class BaseModelClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        pass


class KimiClient(BaseModelClient):
    def __init__(self, api_key: str, model: str = "moonshot-v1-8k"):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        self.model = model

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=settings.MODEL_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS,
            timeout=settings.AI_TIMEOUT,
        )
        return response.choices[0].message.content


MODEL_REGISTRY = {
    "kimi": KimiClient,
}


def get_model_client() -> BaseModelClient:
    provider = settings.MODEL_PROVIDER
    cls = MODEL_REGISTRY.get(provider, KimiClient)
    return cls(settings.MODEL_API_KEY, settings.MODEL_NAME)


SYSTEM_PROMPT = """你是一位专业的儿童发展心理学家和家庭教育顾问。请根据以下亲子评估报告数据，为家长写一份温暖、专业、有行动指导意义的深度解读。

要求：
1. 语气要像一个理解家长焦虑、愿意陪伴他们成长的朋友
2. 不要制造恐慌，但要如实指出需要关注的领域
3. 给出具体、可操作的建议，不要空泛
4. 最后给家长一段真诚的鼓励

请用 Markdown 格式输出，包含以下部分：
## 整体画像
## 核心关切（1-2个最需要优先处理的问题）
## 具体行动（3-5条本周就能做的建议）
## 温暖鼓励
"""


def build_diagnosis_prompt(report_data: Dict[str, Any]) -> str:
    scores = report_data.get("scores", {})
    dim_analysis = report_data.get("dimension_analysis", {})
    summary = report_data.get("summary", "")
    flags = report_data.get("flags", [])
    dim_lines = []
    for dim, score in scores.items():
        analysis = dim_analysis.get(dim, {})
        level = analysis.get("level", "")
        dim_lines.append(f"- {analysis.get('dim_name', dim)}: {score}分 ({level})")
    prompt = f"""【孩子年龄段】: {report_data.get('meta', {}).get('name', '')}

【各维度得分】:
{chr(10).join(dim_lines)}

【整体摘要】: {summary}

【红旗信号】: {len(flags)}个
"""
    if flags:
        for f in flags:
            prompt += f"- [{f.get('dim', '')}] {f.get('question', '')}\n"
    lowest_dim = min(scores.items(), key=lambda x: x[1])[0]
    lowest_name = dim_analysis.get(lowest_dim, {}).get("dim_name", lowest_dim)
    prompt += f"\n【最弱维度】: {lowest_name}（{scores.get(lowest_dim, 0)}分）\n"
    return prompt

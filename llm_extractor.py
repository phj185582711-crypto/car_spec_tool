
from zhipuai import ZhipuAI
import json
import os
from typing import List, Dict

# 从环境变量读取API Key
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
if not ZHIPU_API_KEY:
    raise ValueError("⚠️  ZHIPU_API_KEY environment variable not found!")

MODEL_NAME = "glm-4-flash"
client = ZhipuAI(api_key=ZHIPU_API_KEY)

def extract_specs_from_text(text: str, page_num: int) -> List[Dict]:
    """
    Extract technical specifications from text with Zhipu LLM
    """
    # 100%全英文Prompt，彻底避免中文编码问题
    prompt = f"""
You are a senior automotive system requirements engineer.
Your ONLY task is to extract ALL technical specifications from the following page {page_num} document content.

Each specification MUST be a JSON object with 3 mandatory fields:
- spec_name: Clear name of the specification (e.g., "Low Beam Efficacy", "Working Temperature Range")
- spec_value: Exact value of the specification (e.g., "≥85lm/W", "-40℃~105℃")
- spec_type: Type of specification (MUST be one of: performance, regulation, interface, environment, reliability)

RULES:
1. Output ONLY a valid JSON array, NO other text, explanations or comments
2. If no specifications found, output empty array: []
3. Keep spec_name and spec_value as exact as possible from the original text

EXAMPLE INPUT:
"Low beam efficacy ≥85lm/W, illumination at 75m ≥20lx, compliant with GB 4599 standard"

EXAMPLE OUTPUT:
[
    {{"spec_name": "Low Beam Efficacy", "spec_value": "≥85lm/W", "spec_type": "performance"}},
    {{"spec_name": "75m Illumination", "spec_value": "≥20lx", "spec_type": "performance"}},
    {{"spec_name": "Compliance Standard", "spec_value": "GB 4599", "spec_type": "regulation"}}
]

NOW PROCESS THIS CONTENT:
---
{text}
---
    """.strip()

    try:
        # 调用智谱API，强制用UTF-8编码
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}  # ✅ 移除了 headers
        )


        # 解析API返回
        response_content = response.choices[0].message.content.strip()
        result_json = json.loads(response_content)

        # 兼容模型输出格式
        specs = result_json if isinstance(result_json, list) else []
        if isinstance(result_json, dict):
            for val in result_json.values():
                if isinstance(val, list):
                    specs = val
                    break

        # 给每个指标加页码
        for spec in specs:
            spec["page_num"] = page_num

        print(f"✅ Page {page_num}: Extracted {len(specs)} specifications")
        return specs

    except Exception as e:
        print(f"❌ Page {page_num} extraction failed: {str(e)}")
        return []

# 测试代码
if __name__ == "__main__":
    test_text = """
    Low beam efficacy ≥85lm/W, illumination at 75m ≥20lx
    ADB supports 84 pixel zones, glare suppression rate ≥90%
    Protection class IP6K7, compliant with GB 4599 standard
    """
    test_result = extract_specs_from_text(test_text, page_num=1)
    print(json.dumps(test_result, ensure_ascii=False, indent=2))
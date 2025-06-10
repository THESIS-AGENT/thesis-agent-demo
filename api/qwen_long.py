from openai import OpenAI
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import ali_bailian_api_key

def query_qwen_long(prompt):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=ali_bailian_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model = "qwen-long",
        messages=[
            {"role": "user", "content": prompt}
            ]
    )
    return completion.choices[0].message.content

# 测试用例
if __name__ == "__main__":
    print(query_qwen_long("你好?"))

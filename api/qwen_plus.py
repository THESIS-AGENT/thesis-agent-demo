from openai import OpenAI
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import ali_bailian_api_key

def query_qwen_plus(prompt):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=ali_bailian_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model = "qwen-plus",
        messages=[
            {"role": "user", "content": prompt}
            ]
    )
    return completion.choices[0].message.content

# 测试用例
if __name__ == "__main__":
    tmp_prompt = """请判断tag: abstract与tag: context的内容的相关性, 并直接返回一个相关性得分(属于0到100的正整数), 如果两个内容是强相关则是100分, 如果两个内容完全无关则认为是0分. 
    无需任何解释或说明. 你认为abstract与context的内容相关性得分为:
    """
    # tmp_response = query_qwen_plus("<abstract>三维晶粒长大速率方程的大尺度Potts模型Monte Carlo仿真验证<abstract>\n<context>同时，通过优化的抽帧策略与推理加速技术，系统能够在保证决策质量的同时将延迟控制在100ms以内，达到了实时交互的要求<context>" + tmp_prompt)
    tmp_response = query_qwen_plus("<abstract>自动驾驶技术<abstract>\n<context>从早期的辅助驾驶系统到今天的高级自动驾驶技术，这一领域已经取得了显著进步</context>" + tmp_prompt)
    print(tmp_response)

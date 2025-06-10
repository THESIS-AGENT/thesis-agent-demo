from openai import OpenAI
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import ali_bailian_api_key

def query_qwen_qwq(prompt):
    """
    向千问QwQ模型发送请求并获取回复
    
    参数:
        prompt (str): 用户输入的提示
        model (str): 要使用的模型名称，默认为 'qwq-32b'
        api_key (str, optional): API密钥，如不提供则从环境变量获取
        
    返回:
        dict: 包含思考过程和回复内容的字典
    """
    # 初始化OpenAI客户端
    client = OpenAI(
        api_key = ali_bailian_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""     # 定义完整回复
    is_answering = False    # 判断是否结束思考过程并开始回复

    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model="qwq-32b",  # 可通过参数更换模型名称
        messages=[
            {"role": "user", "content": prompt}
        ],
        # QwQ 模型仅支持流式输出方式调用
        stream=True,
    )

    for chunk in completion:
        # 如果chunk.choices为空，跳过
        if not chunk.choices:
            continue
        else:
            delta = chunk.choices[0].delta
            # 获取思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                reasoning_content += delta.reasoning_content
            else:
                # 开始回复
                if delta.content != "" and is_answering is False:
                    is_answering = True
                # 累积回复内容
                answer_content += delta.content

    return answer_content

# 测试用例
if __name__ == "__main__":
    print(query_qwen_qwq("9.9和9.11谁大"))
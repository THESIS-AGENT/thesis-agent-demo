import sys
import requests
import urllib3
import socket
import socks
from pathlib import Path

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 可选：配置SOCKS5代理（如果需要）
# 如果您需要使用代理，请取消下面两行注释并修改代理地址和端口
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 7890)
# socket.socket = socks.socksocket

# 设置项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import openai_api_key

from openai import OpenAI

def query_openai_o1(prompt):
    client = OpenAI(api_key = openai_api_key)
    completion = client.chat.completions.create(
        model="o1",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    with open("tmp.txt", 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    from template.part_one_template import part_one_template
    tmp_prompt = "请为我围绕tag: experimental_design中的内容, 参照tag: part_one_template的设计思路与实现逻辑, 拆分出该篇论文\"第2章 相关理论与技术\"所需的数据结构: part_two_template = "
    tmp_response = query_openai_o1("<part_one_template> part_one_template = " + str(part_one_template) + "<\part_one_template>\n<experimental_design>" + markdown_text + "<\experimental_design>" + tmp_prompt)
    with open("tmp_response.txt", "a") as f:
        f.write(tmp_response)
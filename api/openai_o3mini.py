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

def query_openai_o3mini(prompt):
    client = OpenAI(api_key = openai_api_key)
    completion = client.chat.completions.create(
        model="o3-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    with open("tmp.txt", 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    tmp_prompt = """<prior_task>你是一名人工智能领域的专家, 请为我基于tag: experimental_design中的内容, 构建论文"2.1 浓烟环境中的视觉退化原理", 阐述浓烟对可见光成像的散射、吸收和偏振扰动等机理，使得传统单模态视觉在烟雾环境下大幅退化的原因，说明本研究引入多模态感知的必要性。请不要再继续向下划分章节. 且尽可能的包含细节和公式.
    请优先保证生成内容的质量达标, 且满足论文书写标准与文风尽量自然, 无需简洁, 可以适当赘述, 再去考量secondary_task的内容.</prior_task>
    <secondary_task>
    请在优先保证tag: prior_task生成的内容原文质量达标的前提下, 找到所有需要添加论文引用的部分、latex公式的部分、以及章节标题或其他需要强调的部分, 基于如下规则添加标识符, 请注意, 你无需联网搜索, 你只需要在原文中做出对应新增:

# 规则一: 对于每个潜在的需要添加论文引用的内容, 面向基于关键字论文搜索引擎进行关联词抽取, 并将这些关联词基于下述的过滤逻辑放入嵌套数组topic_high中, 并在嵌套数组的两头添加上citation标志, 并将<citation>topic_high</citation>放置在原文中需要添加引用标志的位置.
topic_high为联合搜索关联词列表, 这个字段采用python嵌套数组的格式，样例如: [['关联词1', '关联词2', ...], ['关联词3', ...], ...]
数组最多只允许一次嵌套, 最小数组里的逻辑为or，最小数组外的逻辑为and, 对于上述样例, 查找的逻辑即为(关联词1 ∩ 关联词2) ∪ (关联词3). 每个关联词既可以是英文也可以是中文, 即可以是应用场景, 也可以是技术点. 使用并组合这些关键词的目标应该是使后续工作流可以按照topic_high想要传达的逻辑尽可能精准的找到目标论文.
后续工作流(无需你来关心和实现)将会通过这个topic_high来调用论文关键字搜索引擎. 将匹配到最为符合的top1的论文作为目标论文, 并使用其引用内容替换掉文章此处的内容. 

# 规则二: 对每个latex公式的开头位置与终止位置添加标志, 即latex公式需要包含在<formula>...</formula>之间.

# 规则三: 对于每个原文中的标题, 请参考其层级, 在头部添加Markdown格式的井号; 对于每个有必要加粗或者变为斜体的部分(tag: formula以及tag: citation的内容并不适用于这种情况), 请在头部和尾部同时添加Markdown格式的单个或双个星号.
</secondary_task>"""
    tmp_response = query_openai_o3mini("<experimental_design>" + markdown_text + "<\experimental_design>" + tmp_prompt)
    with open("tmp_response_o3mini.txt", "a") as f:
        f.write(tmp_response)
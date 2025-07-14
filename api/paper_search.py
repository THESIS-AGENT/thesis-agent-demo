import requests
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import Aminer_openPlatform_api_key

import json

# Search for papers
def search_papers(query, size):
    url = "https://datacenter.aminer.cn/gateway/open_platform/api/paper/qa/search"
    
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": Aminer_openPlatform_api_key
    }
    
    data = {
        # （较慢）自然语言原始问题，如果开启，会将此问题拆分关键词后查找论文。如果同时传入topic_high等关键词时，以此参数获得的关键词为准
        # "query": query,
        # use_topic必须为true时可使用，联合搜索词列表,在搜索词里必须出现的，使用嵌套数组json格式，样例如
        # [['相变储能', 'phase change energy storage', 'PCM'], ['量子化学计算', 'quantum chemistry calculation']
        # 最小数组里为or，最小数组外为and
        'topic_high': json.dumps(query, ensure_ascii=False),
        # 如果开启，会给引用量大的进行加分
        "n_citation_flag": False,
        # 完全按照citation排序
        "force_citation_sort": False,
        # 完全按照year排序
        "force_year_sort": False,
        # 是否使用联合搜索。如果为true，则使用topic字段进行搜索。
        "use_topic": True,
        "size": size,
        # 有一些经典论文可能年限比较早了.
        # "year": [2025, 2024, 2023, 2022]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Get paper details
def get_paper_details(paper_id):
    url = f"https://datacenter.aminer.cn/gateway/open_platform/api/paper/detail?id={paper_id}"
    
    headers = {
        "Authorization": Aminer_openPlatform_api_key
    }
    
    response = requests.get(url, headers=headers)
    return response.json()


if __name__ == "__main__":
    # print(search_papers("浓烟环境人体目标判别：基于多模态融合与Qwen2-VL模型的智能检测方案", 10))
    print(search_papers([['浓烟', '散射', '可见光退化'], ['smoke', 'scattering', 'vision degradation']], 10))
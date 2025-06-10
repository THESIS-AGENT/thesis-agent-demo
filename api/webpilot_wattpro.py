import requests
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import wattpro_api_key
import json

def query_wattpro(prompt):
    data = {
        "model": "watt-pro",
        "content": prompt
    }
    headers = {
        "Authorization": f"Bearer {wattpro_api_key}"
    }
    rsp = requests.post("https://beta.webpilotai.com/api/v1/watt", json=data, headers=headers)
    response_text = rsp.content.decode('utf-8')
    response_json = json.loads(response_text)
    return response_json["content"]

if __name__ == "__main__":
    print(query_wattpro("请为我搜索多模态数据融合的基本概念、方法和应用，重点探讨如何在不同模态之间进行特征融合和信息互补，以提升目标检测的精度"))
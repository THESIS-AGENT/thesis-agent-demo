import http.client
import json

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import serper_api_key

def query_singleWebsite(url, includeMarkdown=True, tolerance=3):
    # 添加重试逻辑，最多重试tolerance次
    retry_count = 0
    
    while retry_count <= tolerance:
        try:
            """
            输入url
            """
            conn = http.client.HTTPSConnection("scrape.serper.dev")
            payload = json.dumps({
            "url": url,
            "includeMarkdown": includeMarkdown
            })
            headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
            }
            conn.request("POST", "/", payload, headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data)
            return json_data
        except Exception as e:
            print("[serper_normal]", e)
    raise Exception(f"serper API失败，已重试{tolerance}次.")

if __name__ == "__main__":
    pass
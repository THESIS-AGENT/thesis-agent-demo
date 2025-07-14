import sys
import requests
import urllib3
import socket
import socks
from pathlib import Path
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 可选：配置SOCKS5代理（如果需要）
# 如果您需要使用代理，请取消下面两行注释并修改代理地址和端口
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 7890)
# socket.socket = socks.socksocket

# 设置项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import claude_api_key

def query_claude(prompt, tolerance=1):
    """
    调用Claude API获取响应
    参数:
        prompt (str): 发送给Claude的提示文本
    返回:
        str: Claude的回复文本
    """
    # 配置API请求
    headers = {
        "x-api-key": claude_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 23333,
        "temperature": 1,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    # 添加重试逻辑，最多重试tolerance次
    retry_count = 0
    
    while retry_count <= tolerance:
        try:
            # 发送API请求
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=333
            )
            
            response.raise_for_status()  # 如果状态码不是200，将抛出HTTPError异常
            result = response.json()
            return result['content'][0]['text']
            
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            retry_count += 1
            if retry_count <= tolerance:
                print(f"[api.claude_37] 请求失败: {e} \n正在进行第{retry_count}次重试...")
                time.sleep(33)  # 重试前等待2秒
            else:
                # 已达到最大重试次数，抛出异常
                raise Exception(f"请求Claude API失败，已重试{tolerance}次: {str(e)}")

if __name__ == "__main__":
    # 测试模块功能
    print(query_claude("我现在的想法现在目前是TCN整飞行参数的编码器，Vit做视频的编码器. TCN指的是什么?"))
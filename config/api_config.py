import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 阿里-百炼
# 从环境变量读取，或设置为您的API密钥
ali_bailian_api_key = os.getenv("ALI_BAILIAN_API_KEY", "your_ali_bailian_api_key_here")

# https://open.aminer.cn/open/board?tab=control
# AMiner开放平台API密钥
Aminer_openPlatform_api_key = os.getenv("AMINER_API_KEY", "your_aminer_api_key_here")

# https://console.anthropic.com/settings/billing
# Claude API密钥
claude_api_key = os.getenv("CLAUDE_API_KEY", "your_claude_api_key_here")

# https://www.webpilot.ai/developer/dashboard/documents/watt
# WebPilot WattPro API密钥
wattpro_api_key = os.getenv("WATTPRO_API_KEY", "your_wattpro_api_key_here")

# https://platform.openai.com/settings/organization/api-keys
# OpenAI API密钥
openai_api_key = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# https://serper.dev/logs
# Serper API密钥
serper_api_key = os.getenv("SERPER_API_KEY", "your_serper_api_key_here")

# https://app.tavily.com/home
# Tavily API密钥
tavily_api_key = os.getenv("TAVILY_API_KEY", "your_tavily_api_key_here")
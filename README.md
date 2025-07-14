# 论文范文写作助手 (Paper Writing Assistant)

一个基于多个大语言模型的智能论文范文写作系统，能够根据输入的开题报告或研究设计文档，自动生成完整的学术论文各章节内容，作为写作参考或起点。

## 🚀 项目特色

- **多模型协作**: 集成OpenAI、Claude、阿里通义千问等多个先进的大语言模型
- **智能流水线**: 采用多阶段处理流程，确保论文质量和逻辑连贯性
- **自动化生成**: 从开题报告到完整论文的全自动化处理
- **格式规范**: 输出标准的学术论文格式，支持Word文档
- **质量控制**: 内置反馈机制和质量检查，确保生成内容的准确性和可读性

## 🛠️ 技术栈

### 核心技术
- **Python 3.8+**: 主要开发语言
- **多个LLM API**: OpenAI GPT、Claude、通义千问等
- **文档处理**: python-docx用于Word文档操作
- **网络搜索**: Serper、Tavily API用于学术资料检索
- **并发处理**: 支持多模型并行调用

### 主要依赖
- `openai`: OpenAI API客户端
- `anthropic`: Claude API客户端  
- `python-docx`: Word文档处理
- `requests`: HTTP请求处理
- `tqdm`: 进度条显示
- `python-dotenv`: 环境变量管理

## 📦 安装指南

### 1. 克隆项目
```bash
git clone <repository-url>
cd paper_agent
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置API密钥
复制环境变量示例文件并配置您的API密钥：
```bash
cp env.example .env
```

编辑 `.env` 文件，填入您的实际API密钥：
```env
# 必需的API密钥
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# 可选的API密钥（用于增强功能）
ALI_BAILIAN_API_KEY=your_ali_bailian_api_key_here
SERPER_API_KEY=your_serper_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 🎯 使用方法

### 基本使用流程

1. **准备输入文档**
   - 将您的开题报告或研究设计文档（.docx格式）放入 `input/` 目录
   - 确保文档包含研究背景、目标、方法等关键信息

2. **修改配置**
   - 编辑 `pipeline.py` 文件中的输入路径：
   ```python
   input_docx_path = "./input/your_document.docx"  # 替换为您的文档路径
   ```

3. **运行生成流程**
   ```bash
   python pipeline.py
   ```

4. **查看输出结果**
   - 生成的论文范文将保存在 `output/` 目录中
   - 包含各章节的 Word 文档和中间处理文件，可用于参考和撰写指导

### 高级使用

#### 单独运行各个模块

**预处理阶段**（提取和分析输入文档）：
```bash
python pipeline_pre.py
```

**第一章生成**（绪论部分）：
```bash
python pipeline_chapter1.py
```

**第二章生成**（相关理论与技术）：
```bash
python pipeline_chapter2.py
```

#### 自定义配置

您可以修改以下配置文件来自定义行为：
- `config/global_config.py`: 全局配置参数
- `template/global_template.py`: 论文模板和提示词
- `template/part_one_template.py`: 第一章模板

## 📁 项目结构

```
paper_agent/
├── api/                    # API调用模块
│   ├── openai_o1.py       # OpenAI O1模型
│   ├── openai_o3mini.py   # OpenAI O3-mini模型
│   ├── claude_37.py       # Claude 3.7模型
│   ├── qwen_*.py          # 通义千问系列模型
│   └── serper_normal.py   # 网络搜索API
├── config/                 # 配置文件
│   ├── api_config.py      # API密钥配置
│   └── global_config.py   # 全局配置
├── template/               # 模板文件
│   ├── global_template.py # 全局模板
│   └── part_one_template.py # 第一章模板
├── tools/                  # 工具模块
│   ├── deep_research.py   # 深度研究工具
│   ├── make_bibliography.py # 参考文献生成
│   └── markdown2docx_converter.py # 格式转换
├── utils/                  # 工具函数
│   ├── chapter1_utils.py  # 第一章工具函数
│   ├── chapter2_utils.py  # 第二章工具函数
│   └── pre_utils.py       # 预处理工具函数
├── input/                  # 输入文件目录
├── output/                 # 输出文件目录
├── cases/                  # 历史案例存档
├── pipeline.py            # 主流水线
├── pipeline_pre.py        # 预处理流水线
├── pipeline_chapter1.py   # 第一章生成流水线
├── pipeline_chapter2.py   # 第二章生成流水线
├── requirements.txt       # 依赖包列表
├── env.example           # 环境变量示例
└── README.md             # 项目说明文档
```

## ⚙️ 配置说明

### API密钥获取

1. **OpenAI API**: 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Claude API**: 访问 [Anthropic Console](https://console.anthropic.com/)
3. **通义千问**: 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
4. **Serper API**: 访问 [Serper.dev](https://serper.dev/)
5. **Tavily API**: 访问 [Tavily](https://app.tavily.com/)

### 代理配置（可选）

如果您需要使用代理访问API，可以在相关API文件中取消注释代理配置：

```python
# 在 api/openai_o1.py 和 api/claude_37.py 中
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 7890)
socket.socket = socks.socksocket
```

## 🔧 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确配置
   - 确认网络连接正常
   - 查看API配额是否充足

2. **文档处理错误**
   - 确保输入文档为有效的.docx格式
   - 检查文档是否包含必要的内容结构

3. **依赖安装问题**
   - 使用Python 3.8或更高版本
   - 确保虚拟环境正确激活

### 日志和调试

项目会在控制台输出详细的处理日志，包括：
- API调用状态
- 处理进度
- 错误信息和重试次数

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 开发环境设置
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见LICENSE文件

## ⚠️ 免责声明

本工具仅用于学术研究与教育目的，例如生成写作参考材料、构建范文草稿或辅助文献整理等。使用者应确保：
- 遵守学术诚信与所在机构的行为规范
- 将输出内容用于写作学习、结构分析或内容规划参考
- 对生成内容进行必要的人工审查和个性化修改
- 承担使用本工具的全部责任

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 请确保您有合法权限使用相关的API服务，并遵守各服务提供商的使用条款。 

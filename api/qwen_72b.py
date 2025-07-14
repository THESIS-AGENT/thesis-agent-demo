from openai import OpenAI
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.api_config import ali_bailian_api_key
from openai._exceptions import APIError, APITimeoutError, APIConnectionError
import time

def query_qwen_72b(prompt, specified_model = "qwen-max-latest", tolerance=3, sleep_time=180):
    attempt = 0
    while attempt < tolerance:
        try:
            client = OpenAI(
                # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                api_key=ali_bailian_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                timeout=333
            )

            completion = client.chat.completions.create(
                # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                # model="qwen2.5-72b-instruct",
                model = specified_model,
                messages=[
                    {"role": "user", "content": prompt}
                    ]
            )
            return completion.choices[0].message.content
            
        except (APIError, APITimeoutError, APIConnectionError) as e:
            attempt += 1
            if attempt < tolerance:
                print(f"连接错误: {str(e)}. 尝试 {attempt}/{tolerance}. 等待{int(sleep_time/60)}分钟后重试...")
                time.sleep(sleep_time)
            else:
                print(f"已尝试{tolerance}次，仍然失败: {str(e)}")
                raise e

# 测试用例
if __name__ == "__main__":
    tmp = """请判断当前输入的论文相关内容中是否清晰的给出了实验背景说明（例如发展现状、当前技术的局限性、研究问题的提出、实验的必要性、现实意义等背景信息）, 请直接给出结论true/false

<content>农业采摘机器人VLA建模实现实验方案
一、实验目标
1. 构建面向草莓/蓝莓采摘的端到端VLA模型，支持自然语言指令→视觉感知→动作决策全流程。
2. 验证多阶段微调策略（视觉头微调→知识注入→动作对齐）对模型性能的提升。
3. 探索数据增强策略（遮挡模拟、课程学习、蒸馏SFT）对复杂场景适应性的影响。

二、数据集构建
1. 数据采集与处理
数据类型	规模	采集方法	标注内容
草莓/蓝莓图像	各1500张	真实场景（广州从化基地）+ UE5合成数据	实例分割掩膜、成熟度（0-1）、遮挡等级（低/中/高）
农业知识文本	？条	农业论文、种植手册 + GPT-4生成合成数据	病虫害防治、成熟度判断规则、采摘规范等
动作决策序列	？组	PyBullet仿真生成 + 专家规则标注	抓取位姿（x,y,z,q）、夹爪力度、路径轨迹
VQA多模态数据	？组	人工编写 + ChatGPT-4o生成（图像-问题-答案）	如“左下图草莓是否可采摘？需多大力度？”

2. 数据增强策略
Pipeline ①：遮挡场景模拟
方法：使用分割掩膜随机覆盖20%-70%果实区域（模拟枝叶遮挡）。  
对比实验：对比有无遮挡数据训练的模型在测试集的决策准确率（mAP@0.5）。  

Pipeline ②：课程学习（Curriculum Learning） 
阶段划分：  
Easy：单目标无遮挡 → Medium：多目标轻度遮挡 → Hard：密集簇+动态障碍。  
训练策略：按难度递增顺序分批次输入数据，loss权重逐步增加。  

Pipeline ③：蒸馏SFT（Distilled Supervised Fine-Tuning） 
教师模型：ChatGPT-4o生成图像描述与决策建议（如“建议以4N力度抓取右上草莓”）。  
学生模型：MiniCPM-V/Qwen-VL微调对齐教师输出。  

三、模型选择与微调策略
1. 基座模型
视觉-语言模型：OpenBMB/MiniCPM-V（2.8B）或Qwen/Qwen2.5-VL-3B-Instruct  
选择理由：支持端侧部署，多模态对齐能力优秀，兼容Hugging Face生态。  

2. 分阶段微调
(1) 阶段一：视觉头微调
目标：提升模型对草莓/蓝莓的视觉特征提取能力。  
数据：草莓/蓝莓图像数据集（含分割掩膜）。  
方法：冻结LLM参数，仅微调视觉编码器（ViT）与跨模态投影层。  
损失函数：分割损失（Dice Loss）+ 成熟度回归损失（MSE）。  

(2) 阶段二：知识注入微调
目标：注入农业领域知识（成熟度规则、采摘禁忌）。  
数据：农业知识文本 + VQA多模态数据。  
方法：
①指令微调：以“根据以下知识回答问题：{知识}，问题：{问题}”格式训练。
②检索增强：集成农业知识库（FAISS索引），实现实时知识检索。  

(3) 阶段三：动作决策对齐微调
目标：将语言指令映射为可执行动作参数。  
数据：多模态动作决策数据集（图像-指令-动作序列）。  
方法：  
动作编码：将抓取位姿、力度等参数转换为文本描述（如“move_to(0.5,0.2,0.3), force=4.0”）。  
损失函数：动作序列预测交叉熵损失 + 物理约束正则项（如力度与成熟度匹配）。  

四、动作颗粒度与接口设计
1. 动作颗粒度定义
层级	颗粒度	示例	对齐方式
高级指令	自然语言	采摘所有成熟草莓	模型直接输出
原子动作	机械臂可执行指令	move_to(x,y,z,q), grasp(force=4.0)	参考Unitree运动接口文档标准化格式
控制信号	电机控制参数	关节角、扭矩、速度	仿真/实机驱动层转换
2. 接口文档设计
输入规范：支持文本指令（中英文）或语音转文本。  
输出规范：JSON格式原子动作序列，兼容PyBullet/ROS：  
错误码定义：包含视觉丢失（ERR_VISION_LOST）、路径冲突（ERR_COLLISION）等。  
五、实验设计与评估
1. 对比实验
实验组	训练策略	评估指标
Baseline	原始预训练模型（无微调）	mAP@0.5, 指令跟随准确率
Ours (Full)	三阶段微调 + 数据增强	同上 + 动作执行成功率
Ablation: 无遮挡模拟	移除Pipeline①遮挡数据	遮挡场景mAP下降幅度
Ablation: 无课程学习	随机数据输入（非难度递增）	Hard场景成功率差异

2. 评估指标
感知精度：mAP@0.5（目标≥85%）。  
决策准确率：动作序列与专家标注的编辑距离（目标≤2）。  
执行成功率：PyBullet仿真中成功采摘比例（目标≥90%）。  
推理速度：端侧部署后单帧处理时间（目标≤200ms）。  

六、规划与预期成果
1. 规划
阶段	预期效果
数据采集与标注	完成多模态数据集构建
模型微调与优化	各阶段微调模型达到基线指标
仿真验证与接口对接	实现PyBullet动作执行闭环
论文撰写与成果整理	完成实验对比与消融分析

2. 预期成果
学术成果：1篇论文（聚焦多阶段微调与数据增强策略）。  
代码与模型：开源VLA模型代码与接口文档（GitHub）。  
应用价值：为农业机器人提供低成本智能决策方案，降低人工依赖。</content>"""
    print(query_qwen_72b(tmp))

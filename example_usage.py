#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文代写助手使用示例

这个文件展示了如何使用论文代写助手的基本功能。
"""

import os
from pipeline_pre import pipeline_pre
from pipeline_chapter1 import pipeline_chapter1
from pipeline_chapter2 import pipeline_chapter2

def main():
    """
    主函数：演示完整的论文生成流程
    """
    
    # 1. 检查输入文件是否存在
    input_file = "./input/your_document.docx"
    
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        print("请将您的开题报告或研究设计文档放入 input/ 目录中")
        return
    
    # 2. 确保输出目录存在
    os.makedirs("./output", exist_ok=True)
    
    try:
        print("开始论文生成流程...")
        
        # 3. 预处理阶段：分析输入文档，生成实验设计
        print("第1步：预处理和实验设计生成...")
        pipeline_pre(input_file, "./output/pre_output.txt")
        print("✓ 预处理完成")
        
        # 4. 生成第一章：绪论
        print("第2步：生成第一章（绪论）...")
        pipeline_chapter1()
        print("✓ 第一章生成完成")
        
        # 5. 生成第二章：相关理论与技术
        print("第3步：生成第二章（相关理论与技术）...")
        pipeline_chapter2("./output/pre_output.txt", "./output/part_two_template.py")
        print("✓ 第二章生成完成")
        
        print("\n🎉 论文生成完成！")
        print("请查看 output/ 目录中的生成文件：")
        print("- pre_output.docx: 实验设计部分")
        print("- 第一章中间步.docx: 第一章内容")
        print("- 第二章中间步.docx: 第二章内容")
        
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {str(e)}")
        print("请检查：")
        print("1. API密钥是否正确配置")
        print("2. 网络连接是否正常")
        print("3. 输入文档格式是否正确")

def check_environment():
    """
    检查环境配置是否正确
    """
    print("检查环境配置...")
    
    # 检查必需的API密钥
    required_keys = ['OPENAI_API_KEY', 'CLAUDE_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key) or os.getenv(key) == f"your_{key.lower()}_here":
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ 缺少必需的API密钥配置:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n请在 .env 文件中配置这些API密钥")
        return False
    
    print("✓ 环境配置检查通过")
    return True

if __name__ == "__main__":
    # 检查环境配置
    if check_environment():
        # 运行主程序
        main()
    else:
        print("\n请先配置必需的API密钥，然后重新运行此脚本。")
        print("参考 README.md 文件中的配置说明。") 
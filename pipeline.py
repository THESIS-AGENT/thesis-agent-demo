from pipeline_pre import pipeline_pre
from pipeline_chapter2 import pipeline_chapter2
from pipeline_chapter1 import pipeline_chapter1
import os
import shutil
from datetime import datetime
from tools.make_bibliography import make_bibliography

if __name__ == "__main__":
    # 检查output文件夹是否存在
    output_dir = "./output"
    if not os.path.exists(output_dir):
        # 如果不存在则创建
        os.makedirs(output_dir)
        print(f"已创建文件夹: {output_dir}")
    else:
        # 如果存在则移动到cases目录并按当前时间重命名
        # 确保cases目录存在
        cases_dir = "./cases"
        if not os.path.exists(cases_dir):
            os.makedirs(cases_dir)
            
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%m%d_%H%M")
        new_dir_name = f"output_{current_time}"
        new_dir_path = os.path.join(cases_dir, new_dir_name)
        
        # 移动并重命名文件夹
        shutil.move(output_dir, new_dir_path)
        print(f"已将 {output_dir} 移动到 {new_dir_path}")
        
        # 重新创建output文件夹
        os.makedirs(output_dir)
        print(f"已重新创建文件夹: {output_dir}")
        
    # 请将此路径替换为您的输入文档路径
    input_docx_path = "./input/your_document.docx"  # 替换为实际的输入文档路径
    pipeline_pre(input_docx_path, "./output/pre_output.txt")
    pipeline_chapter1()
    # make_bibliography("第1章 绪论", "./output/第一章中间步.docx")
    pipeline_chapter2("./output/pre_output.txt", "./output/part_two_template.py")
    # make_bibliography("第2章 相关理论与技术", "./output/第二章中间步.docx")



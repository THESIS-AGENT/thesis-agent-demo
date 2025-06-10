from api.openai_o1 import query_openai_o1
from template.part_one_template import part_one_template
from utils.chapter2_utils import *
from api.qwen_72b import query_qwen_72b
from api.openai_o3mini import query_openai_o3mini
from tqdm import tqdm

import os
from tools.make_bibliography import make_bibliography
    
def pipeline_chapter2(draft_path, part_two_template_pyPath = "./output/part_two_template.py"):
    """draft_path是开题报告->实验设计后, 实验设计的纯文本txt路径,
    后续的链路都微淘实验设计来做.
    
    part_two_template_pyPath是指向第二章的模板文件的储存路径."""
    
    with open(draft_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    
    # 剔除多余干扰字段, 这些字段对于part_two_template无用.
    clean_part_one_template = clean_template(part_one_template)
    
    # 实验设计->第二章的模板文件
    prompt4constructing_part_two_template = "请为我围绕experimental_design标签中的内容, 在层级不超过3的颗粒度下(即段落结构最深为'1.1.1'), 参照part_one_template标签中目录模板的数据结构设计思路与实现逻辑, 拆分出该篇论文\"第2章 相关理论与技术\"所需的python数据结构. 请注意, \"段落名\"字段中的内容不能包含诸如\/:*?\"<>|的特殊符号. 请直接给出目标内容: part_two_template = "
    
    part_two_template_str = query_openai_o1("<part_one_template> part_one_template = " + str(clean_part_one_template) + "<\part_one_template>\n<experimental_design>" + markdown_text + "<\experimental_design>" + prompt4constructing_part_two_template)
    part_two_template_str = remove_python_flag(part_two_template_str)
    with open(part_two_template_pyPath, "w") as f:
        f.write(part_two_template_str)

    # 第二章的模板文件->校验->(如果不通过)重做->(如果通过)结构化
    while True:
        part_two_template = get_part_two_template(part_two_template_pyPath)
        if isinstance(part_two_template, str):
            feedback = part_two_template
        else:
            if_flag = validate_part_two_template(part_two_template)
            if if_flag is True:
                # 进行后续操作, 开始生成第二章节.
                break
            else:
                feedback = "在对part_two_template进行数据结构校验时发生: " + if_flag[-1]
        
        prompt4fixing_wrong_part_two_template = "在参照tag: part_one_template的设计思路与实现逻辑来构建符合业务需要的part_two_template后, 在从part_two_template.py引入同名变量, 或对part_two_template的数据结构进行校验时中出现了以下错误: '" + feedback + "'. 请对照这个错误, 检查tag: part_two_template的内容并进行修正, 请直接在回复中给出一个可以完整写入part_two_template.py文件的正确代码内容, 以'part_two_template ='开头, 无需给出任何多余解释和使用示例." 
        part_two_template_str = query_qwen_72b("<part_one_template> part_one_template = " + str(clean_part_one_template) + "<\part_one_template>\n<part_two_template>" + part_two_template_str + "<\part_two_template>" + prompt4fixing_wrong_part_two_template)
        part_two_template_str = remove_python_flag(part_two_template_str)
        with open(part_two_template_pyPath, "w") as f:
            f.write(part_two_template_str)
        print("[pipeline_chapter2] 尝试修正.")
        
    # 第二章的模板文件数据结构->各子段落内容->文件储存
    prompt4singleParagraph = """
    
    你是一名人工智能与计算机领域的专家, 请为我基于experimental_design标签中的实验设计, 构建论文章节"{}"的内容, {}.
    remarks标签中的内容(如果存在的话)仅供参考, 以强调当前章节的关联性, 防止在当前章节生成与前序章节重复的冗余内容.
    
    不要再继续向下划分章节亦或给论点标出序号.
    请尽可能多的包含原理细节和公式描述, 但无需包含任何形式的python代码或伪代码.
    公式的表达方式请遵循LaTeX基本表达式.
    不要包含如数学矩阵环境bmatrix, 数学对齐环境align, 亦或方程组环境array等任何Latex环境.
    请你优先满足论文书写标准. 文风不需要简洁, 而是尽量自然, 可以适当赘述.
    
    对于潜在的可以添加引用的内容部分, 例如需要引用他人的研究成果的部分, 背景和文献综述部分, 对比和分析部分, 观点和主张部分,
    你需要参照工具一的tool_1规则进行生成.
    <tool_1>
    # 工具一: 对于每个可以添加引用的内容部分, 请从关联原文中进行面向"论文搜索引擎"的关键词抽取, 从而使用论文搜索引擎找到此处的最佳引用.
    请将这些关联词添加进关键词数组中, 在python格式的数组的两头添加上citation标志, 并将<citation>["关键词1", "关键词2", ...]</citation>放置在原文中需要添加引用标志的位置 (关键词需要被双引号包含).
    对于上述样例, 查找的逻辑即为关联词1 ∩ 关联词2 ∩ 关联词...
    数组中的关键词既可以都是英文也可以都是中文, 如果都是中文的话, 则是进行中文期刊的检索; 如果都是英文的话, 则是进行英文期刊的检索. 请不要中英混杂.
    每个关键词既可以是应用场景, 也可以是技术点. 使用并组合这些关键词的目标应该是使后续工作流可以按照关键词数组想要传达的查询逻辑尽可能精准的找到目标论文
    后续工作流(无需你来关心和实现)将会通过这个关键词数组来调用论文搜索引擎. 将匹配到最为符合的topN的论文作为目标论文, 并使用其引用内容替换掉文章此处的内容. 
    </tool_1>
    
    对于内容中出现的每一个公式部分, 你需要参照工具二的tool_2规则进行生成.
    <tool_2>
    # 工具二: 请在每个公式的开头位置与终止位置添加formula标志, 即所有公式都需要包含在<formula>...</formula>之间.
    请确保夹杂在文本中的公式也被添加上formula标志.
    </tool_2>
    
    请使用Markdown的格式生成内容, 包括但不限于对于每个原文中的标题, 参考其层级, 在头部添加Markdown格式的井号; 对于每个有必要加粗或者变为斜体的部分(tag: formula以及tag: citation的内容并不适用于这种情况), 在头部和尾部同时添加Markdown格式的单个或双个星号.
    
    请直接给出当前章节的生成的内容, 无需添加任何解释说明: """

    paragraph_title_L1 = part_two_template["content"][0]["段落名"]
    paragraph_task_L1 = part_two_template["content"][0]["段落描述"]

    os.makedirs(f"./output/{paragraph_title_L1}", exist_ok=True)

    for element_ in tqdm(part_two_template["content"][0]["content"]):
        paragraph_title_L2 = element_["段落名"]
        paragraph_task_L2 = element_["段落描述"]
        if "content" in element_:
            previous_title_L3 = None
            previous_task_L3 = None
            for sub_element in element_["content"]:
                paragraph_title_L3 = sub_element["段落名"]
                paragraph_task_L3 = sub_element["段落描述"]
                if previous_task_L3 is None:
                    prompt4previousAccumulation_L3 = f"<remarks>当前章节\"{paragraph_title_L3}\":{paragraph_task_L3}\"属于上级章节\"{paragraph_title_L2}\":{paragraph_task_L2}. 不存在前序同级章节.<remarks>"
                else:
                    prompt4previousAccumulation_L3 = f"<remarks>当前章节\"{paragraph_title_L3}\":{paragraph_task_L3}\"属于上级章节\"{paragraph_title_L2}\":{paragraph_task_L2}. 且存在前序同级章节\"{previous_title_L3}\":{previous_task_L3}. 前序同级章节的内容为<previous_content>{response_1}</previous_content><remarks>"
                    
                previous_title_L3 = paragraph_title_L3
                previous_task_L3 = paragraph_task_L3
                response_1 = query_openai_o3mini("<experimental_design>" + markdown_text + "<\experimental_design>" + prompt4previousAccumulation_L3 + prompt4singleParagraph.format(paragraph_title_L3, paragraph_task_L3))
                # [可改]可在此添加二次润色或校验逻辑.
                with open(f"./output/{paragraph_title_L1}/{paragraph_title_L3}.txt", "w") as f:
                    f.write(response_1)
                    
        else:
            prompt4previousAccumulation_L2 = f"<remarks>当前章节\"{paragraph_title_L2}\":{paragraph_task_L2}\"属于上级章节\"{paragraph_title_L1}\":{paragraph_task_L1}.<remarks>"
            response_2 = query_openai_o3mini("<experimental_design>" + markdown_text + "<\experimental_design>" + prompt4previousAccumulation_L2 + prompt4singleParagraph.format(paragraph_title_L2, paragraph_task_L2))
            # [可改]可在此添加二次润色或校验逻辑.
            with open(f"./output/{paragraph_title_L1}/{paragraph_title_L2}.txt", "w") as f:
                f.write(response_2)

    make_bibliography(paragraph_title_L1, "./output/第二章中间步.docx")


if __name__ == "__main__":
    pass
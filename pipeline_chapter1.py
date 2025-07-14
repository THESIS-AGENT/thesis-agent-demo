from utils.chapter1_utils import *
from tools.deep_research import search_zhihu
from api.openai_o3mini import query_openai_o3mini
from template.part_one_template import part_one_template
from tools.make_bibliography import make_bibliography
from api.claude_37 import query_claude
from tqdm import tqdm
import json
import time
import os


def pipeline_chapter1():
    # 读取论文基本信息
    with open("output/results_json_from_pipelinePre.json", "r") as f:
        results_json_from_pipelinePre = json.load(f)

    paper_title = results_json_from_pipelinePre["论文标题"]

    # --------------------------------生成第一章各个子章节--------------------------------
    tmp_prompt_3 = """<prior_task>
    你是一名人工智能与计算机领域的专家, 请为我围绕这些信息, 构建标题名为"$$$paper_title$$$"的论文章节"{}"的内容, {}
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
    
    tmp_prompt_3 = tmp_prompt_3.replace("$$$paper_title$$$", paper_title)
    
    tmp_prompt_3_1 = """
    basic_info标签中的内容为当前论文的基本信息.
    reference标签中的内容为联网检索得到的相关信息.
    """ + tmp_prompt_3

    tmp_prompt_3_2 = """
    experimental_design标签中的内容为当前论文的实验设计.
    """ + tmp_prompt_3

    tmp_prompt_3_3 = """
    experimental_design标签中的内容为当前论文的实验设计.
    innovation_point标签中的内容为当前论文的创新点划分.
    """ + tmp_prompt_3

    paragraph_title_L1 = part_one_template["content"][0]["段落名"]
    paragraph_task_L1 = part_one_template["content"][0]["段落描述"]
    basic_info = json.dumps(results_json_from_pipelinePre, ensure_ascii=False)
    
    os.makedirs(f"./output/{paragraph_title_L1}", exist_ok=True)

    draft_path = "./output/pre_output.txt"
    with open(draft_path, 'r', encoding='utf-8') as f:
        experimental_design = f.read()

    # --------------------------------生成创新点--------------------------------
    # 生成创新点所使用的.
    tmp_prompt_6 = """
    tag: basic_info的内容为当前论文的基本信息.
    tag: experimental_design的内容为当前论文的实验设计.
    <prior_task>
    你是一名人工智能与计算机领域的专家, 请为我考量如何从前述实验设计的整体思路中凝练出 2～3 个核心创新点。
    实验设计对你的参考意义应该远大于论文基本信息。
    </prior_task>
    请以一个json-list的格式将答案提供给我, list中的每个dict元素需要包含"创新点名称"->str，"创新点所包含的工作内容"->list，"创新点价值"->str 三个字段的内容。
    回复请以```json开头，以```结尾，无需添加任何多余解释和说明。
    """

    tmp_json_str = query_openai_o3mini(f"<basic_info>{basic_info}<basic_info>\n<experimental_design>{experimental_design}</experimental_design>" + tmp_prompt_6)
    innovation_point = extract_json_from_string(tmp_json_str)
    # 存出创新点
    with open('./output/innovation_point_from_pipelineC1.json', 'w', encoding='utf-8') as f:
        json.dump(innovation_point, f, ensure_ascii=False, indent=4)

    for element_ in tqdm(part_one_template["content"][0]["content"]):
        paragraph_title_L2 = element_["段落名"]
        if "if_lag" in element_:
            if element_["if_lag"] is True:
                # 先跳过这一章, 这一章应该全文结束后再生成.
                continue
        if "$$$" in paragraph_title_L2:
            paragraph_title_L2 = get_new_title(paragraph_title_L2, basic_info)
            paragraph_title_L2 = check_title(paragraph_title_L2, basic_info)
            print("#1 论文标题(处理后):", paragraph_title_L2)
        paragraph_task_L2 = element_["段落描述"]
        if "content" in element_:
            previous_title_L3 = None
            previous_task_L3 = None
            for sub_element in element_["content"]:
                if "if_lag" in sub_element:
                    if sub_element["if_lag"] is True:
                        # 先跳过这一子章, 这一子章应该全文结束后再生成.
                        continue
                paragraph_title_L3 = sub_element["段落名"]
                if "$$$" in paragraph_title_L3:
                    paragraph_title_L3 = get_new_title(paragraph_title_L3, basic_info)
                    paragraph_title_L3 = check_title(paragraph_title_L3, basic_info)
                    print("#2 论文标题(处理后):", paragraph_title_L3)
                paragraph_task_L3 = sub_element["段落描述"]
                if previous_task_L3 is None:
                    prompt4previousAccumulation_L3 = f"<remarks>当前章节\"{paragraph_title_L3}\":{paragraph_task_L3}\"属于上级章节\"{paragraph_title_L2}\":{paragraph_task_L2}. 不存在前序同级章节.<remarks>"
                else:
                    prompt4previousAccumulation_L3 = f"<remarks>当前章节\"{paragraph_title_L3}\":{paragraph_task_L3}\"属于上级章节\"{paragraph_title_L2}\":{paragraph_task_L2}. 且存在前序同级章节\"{previous_title_L3}\":{previous_task_L3}. 前序同级章节的内容为<previous_content>{generated_paragraph_1}</previous_content><remarks>"
                previous_title_L3 = paragraph_title_L3
                previous_task_L3 = paragraph_task_L3
                if sub_element["if_tech"]:
                    # 如果当前内容需要围绕实验设计来写, 那么实验设计优先级是最高的, 不受外部任何干扰.
                    # 如果当前内容需要围绕创新点来写, 那么必须要把实验设计塞给它.
                    # 如果当前内容不需要, 那么就把论文基本信息塞给它.
                    if "if_innovation" in element_:
                        inner_prompt_1 = f"<experimental_design>{experimental_design}</experimental_design>\n<innovation_point>{innovation_point}<innovation_point>" + tmp_prompt_3_3.format(paragraph_title_L3, paragraph_task_L3, prompt4previousAccumulation_L3)
                    else:
                        inner_prompt_1 = f"<basic_info>{basic_info}<basic_info>\n<experimental_design>{experimental_design}</experimental_design>" + tmp_prompt_3_2.format(paragraph_title_L3, paragraph_task_L3, prompt4previousAccumulation_L3)
                else:
                    # 查询知乎
                    zhihu_list = search_zhihu(paper_title, paragraph_title_L3, paragraph_task_L3, basic_info, max_retrieval4eachKeyword = 2)
                    # 元素级截断, 防止超长.
                    zhihu_list = get_truncated_zhihu_list(zhihu_list, threshold=16666)
                    inner_prompt_1 = f"<basic_info>{basic_info}<basic_info>\n<reference>{json.dumps(zhihu_list, ensure_ascii=False, indent=4)}</reference>" + tmp_prompt_3_1.format(paragraph_title_L3, paragraph_task_L3, prompt4previousAccumulation_L3)
                try:  
                    generated_paragraph_1 = query_claude(inner_prompt_1)
                except Exception as e:
                    print(e, "#3 claude生成失败, 尝试用o3-mini生成.")
                    generated_paragraph_1 = query_openai_o3mini(inner_prompt_1)
                else:
                    print("#4 claude生成成功.")
                with open(f"./output/{paragraph_title_L1}/{paragraph_title_L3}.txt", "w") as f:
                    f.write(generated_paragraph_1)
                time.sleep(60)
        else:
            prompt4previousAccumulation_L2 = f"<remarks>当前章节\"{paragraph_title_L2}\":{paragraph_task_L2}\"属于上级章节\"{paragraph_title_L1}\":{paragraph_task_L1}.<remarks>"
            if element_["if_tech"]:
                if "if_innovation" in element_:
                    inner_prompt_2 = f"<experimental_design>{experimental_design}</experimental_design>\n<innovation_point>{innovation_point}<innovation_point>" + tmp_prompt_3_3.format(paragraph_title_L2, paragraph_task_L2, prompt4previousAccumulation_L2)
                else:
                    inner_prompt_2 = f"<basic_info>{basic_info}<basic_info>\n<experimental_design>{experimental_design}</experimental_design>" + tmp_prompt_3_2.format(paragraph_title_L2, paragraph_task_L2, prompt4previousAccumulation_L2)
            else:
                # 查询知乎
                zhihu_list = search_zhihu(paper_title, paragraph_title_L2, paragraph_task_L2, basic_info, max_retrieval4eachKeyword = 2)
                # 元素级截断, 防止超长.
                zhihu_list = get_truncated_zhihu_list(zhihu_list, threshold=16666)
                inner_prompt_2 = f"<basic_info>{basic_info}<basic_info>\n<reference>{json.dumps(zhihu_list, ensure_ascii=False, indent=4)}</reference>" + tmp_prompt_3_1.format(paragraph_title_L2, paragraph_task_L2, prompt4previousAccumulation_L2)
            try:
                generated_paragraph_2 = query_claude(inner_prompt_2)
            except Exception as e:
                print(e, "#5 claude生成失败, 尝试用o3-mini生成.")
                generated_paragraph_2 = query_openai_o3mini(inner_prompt_2)
            else:
                print("#6 claude生成成功.")
            with open(f"./output/{paragraph_title_L1}/{paragraph_title_L2}.txt", "w") as f:
                f.write(generated_paragraph_2)
            time.sleep(60)

    make_bibliography(paragraph_title_L1, "./output/第一章中间步.docx")
import docx
from template.global_template import global_template
import json
from api.qwen_72b import query_qwen_72b
from api.qwen_qwq import query_qwen_qwq
from tqdm import tqdm
from api.claude_37 import query_claude
from tools.markdown2docx_converter import MarkdownToDocxConverter
from utils.pre_utils import extract_and_validate_json
from api.openai_o1 import query_openai_o1

def pipeline_pre(docx_path, pre_output_path = "./output/pre_output.txt"):

    # 读取开题报告
    document = docx.Document(docx_path)
    all_paragraphs = document.paragraphs
    paragraph_text= ""
    for paragraph in all_paragraphs:
        paragraph_text += paragraph.text+"\n" 

    user_prompt = global_template["user_prompt"]
    system_prompt = global_template["system_prompt"]

    results_json = {}
    routers_history = []

    """
    备注一: 生成模型和决策模型应该交叉使用, 即使用两个不同的模型.
    """

    for element_ in tqdm(global_template["content"]):
        # 注意, 用户信息在此我标注为"备注信息"remarks
        element_name = element_["element_name"]
        remarks = f"""
        "prior_task"为当前任务目标的字段，需严格执行。
        "system_prompt"为当前系统提示词，需严格参照。
        "remarks"为辅助提示词，若存在有效内容，在不与其他字段冲突和违背的情况下，可以酌情参考。
        "content"为当前任务尚未处理的内容输入，需按照"prior_task"进行处理。
        """
        
        payload = {"remarks": user_prompt, "system_prompt": system_prompt, "content": paragraph_text}
        if element_["if_prompt"] and element_["if_rule"] is not None:
            # 注意, 当前任务目标我标注为"prior_task"
            payload["prior_task"] = element_["if_prompt"]
            # response_1是意图识别中间过程的结果.
            response_1 = query_qwen_72b(json.dumps(payload, ensure_ascii=False, indent=4))
            routers_history.append((element_name, 1))
            # 获得意图识别标识符.
            if_flag_1 = element_["if_rule"](response_1)
            payload["prior_task"] = element_["if_rule_true_prompt" if if_flag_1 else "if_rule_false_prompt"]
            # response_2是第一次尝试生成结果.
            response_2 = query_qwen_72b(json.dumps(payload, ensure_ascii=False, indent=4))
            routers_history.append((element_name, 2))
            # [注意] 暂时还没有融入硬约束逻辑.
            # 如果存在软约束, 即存在要求, 则:
            if element_["soft_constraint"] and element_["feedback"] is not None:
                payload["prior_task"] = element_["soft_constraint"]
                payload[element_name] = response_2
                # response_3是chosen/rejected的中间过程.
                response_3 = query_qwen_qwq(json.dumps(payload, ensure_ascii=False, indent=4))
                routers_history.append((element_name, 3))
                if_flag_2 = element_["feedback"](response_3)
                if if_flag_2 is True:
                    results_json[element_name] = response_2
                    routers_history.append((element_name, 3.5))
                else:
                    # 如果被rejected, 则尝试换一个模型&提示词工程重新生成.
                    payload["prior_task"] = element_["element_prompt"]
                    payload["previous_failure_feedback"] = if_flag_2
                    remarks += f"\"previous_failure_feedback\"字段为\"{element_name}\"中的内容在上一轮评估中未被采纳的原因，其中存在的问题已被指出，你需要在执行当前\"prior_task\"的时候努力避免和改进。"
                    response_4 = query_qwen_qwq(json.dumps(payload, ensure_ascii=False, indent=4))
                    results_json[element_name] = response_4
                    routers_history.append((element_name, 4))
            # [注意] 因为现在都存在软约束, 所以这里暂时不做实现.
            # 未来是硬约束和无约束的逻辑实现位置.
            else:
                pass
        # [注意] 因为现在都存在意图识别, 所以这里暂时不做实现.
        # 未来式无意图识别逻辑的实现位置.
        else:
            pass

    # 用于生成'构建实验设计的提示词'的提示词.
    prompt4experimentPlanGeneration = """请为我设计一套提示词，用于引导大模型能够参照json中的论文相关内容给出详细的实验设计和实施方案。这套提示词应该分为多个部分，按照科学研究的逻辑结构组织，以获取最全面、具体的实验方案。
    请给出可以后续直接使用的提示词，不要提供使用示例或任何添加在开头语结尾的冗余介绍或说明，无需以json的格式给出。"""
    tmp_response_1 = query_qwen_qwq(json.dumps(results_json, ensure_ascii=False, indent=4) + prompt4experimentPlanGeneration)

    # 将全文通用信息存出去.
    with open('./output/results_json_from_pipelinePre.json', 'w', encoding='utf-8') as f:
        json.dump(results_json, f, ensure_ascii=False, indent=4)
    
    # 生成实验设计初稿
    try:
        tmp_response_2 = query_claude(json.dumps(results_json, ensure_ascii=False, indent=4) + tmp_response_1)
    except Exception as e:
        print(e)
        tmp_response_2 = query_openai_o1(json.dumps(results_json, ensure_ascii=False, indent=4) + tmp_response_1)
    with open("./output/pre_output_pre.txt", "w") as f:
        f.write(tmp_response_2)
        
    # 对实验设计, 用推理模型再校验一遍.
    paper_title = results_json["论文标题"]
    prompt4checking_tmp_response_2 = f"""
    当前tag: experimental_design中的内容是论文"{paper_title}"的实验设计.
    请你找出原文中全部的问题, 包含明显错误, 逻辑冲突, 潜在隐患等.
    对于你发现的每一处问题, 你需要指出问题在实验设计中对应的原文片段作为"content"字段, 
    并给出你的问题披露与修改意见作为"feedback"字段.
    请以一个json-list的格式将答案提供给我, list中的每个dict包含"content"和"feedback"两个字段.
    回复请以```json开头，以```结尾，无需添加任何多余解释和说明。
"""
    
    tmp_response_3 = query_qwen_qwq(f"<experimental_design>{tmp_response_2}</experimental_design>" + prompt4checking_tmp_response_2)
    tmp_response_3 = extract_and_validate_json(tmp_response_3)

    with open("./output/tmp_response_3_from_pipelinePre.json", "w") as f:
        f.write(tmp_response_3)
    
    prompt4regenerating = """当前tag: experimental_design中的内容是论文"{paper_title}"的实验设计部分.
    tag: supervisor_comment中包含评审导师给出的反馈意见, 以json格式呈现. 
    其中每个元素的"content"字段为问题在实验设计中对应的原文片段作, "feedback"字段作为问题披露与修改意见.
    请酌情考量实验设计内容中每一个被指明存在问题的原文部分, 与其对应的反馈内容, 
    对于确实存在问题且你认为有必要参照反馈做出修改的部分, 请在直接已有实验设计的内容上做出修改.
    在处理完所有的问题后, 请你直接给出最终的实验设计的全部内容, 并无需添加任何解释说明: 
    """
    
    try:
        tmp_response_4 = query_claude(f"<supervisor_comment>{tmp_response_3}</supervisor_comment>\n<experimental_design>{tmp_response_2}</experimental_design>" + prompt4regenerating)
    except Exception as e:
        print("#1 claude 生成失败, 更换o1.")
        tmp_response_4 = query_openai_o1(f"<supervisor_comment>{tmp_response_3}</supervisor_comment>\n<experimental_design>{tmp_response_2}</experimental_design>" + prompt4regenerating)

    with open(pre_output_path, "w") as f:
        f.write(tmp_response_4)

    # 理论上来讲, 这个文件就是给用户初步感知使用的, 在最终付费前.
    converter = MarkdownToDocxConverter()
    output_file = pre_output_path.replace("txt", "docx")
    converter.convert(tmp_response_4, output_file)
        
if __name__ == "__main__":
    pass
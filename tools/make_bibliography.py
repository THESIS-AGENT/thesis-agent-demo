from glob import glob
import os
import re
from tqdm import tqdm
from utils.chapter2_utils import extract_citations, generate_citation, generate_bibliography, deduplicate_references
import random
from api.paper_search import search_papers, get_paper_details
import json
from tools.markdown2docx_converter import MarkdownToDocxConverter
from api.qwen_plus import query_qwen_plus

def make_bibliography(paragraph_title_L1, output_path):
    # 聚拢当前章节目录下的全部内容, 按照生成的时间顺序, 即真实顺序.
    pathsList = glob(f"./output/{paragraph_title_L1}/*")
    pathsList.sort(key=os.path.getmtime)
    gathered_tmp_text= ""
    for path_ in pathsList:
        with open(path_, 'r', encoding='utf-8') as f:
            tmp_text = f.read()
            gathered_tmp_text += tmp_text+"\n"
        
    # 论文库查找论文->生成论文表&生成引用
    citations = extract_citations(gathered_tmp_text)
    
    replace_dict = {}
    bib_container = []
    index_ = 0
    for cite in tqdm(citations):
        # 随机选择1或2作为当前位置引用的论文数.
        random_number = random.randint(1, 2)
        try:
            search_result_1 = search_papers(eval(cite.replace("<citation>", "").replace("</citation>", "").replace("“", "\"")), random_number)
        except Exception as e:
            print(e, cite)
            continue
        if "data" in search_result_1:
            if search_result_1["data"]:
                for paper_brief in search_result_1["data"]:
                    paper_details = get_paper_details(paper_brief["id"])
                    paper_brief["details"] = paper_details
                    
                    if "data" in paper_details:
                        if paper_details["data"]:
                            # 判断这篇论文的摘要内容是否和当前引用位置的前后文相关.
                            if "abstract_zh" in paper_details["data"][0]:
                                paper_desc = paper_details["data"][0]["abstract_zh"]
                            elif "title_zh" in paper_details["data"][0]:
                                paper_desc = paper_details["data"][0]["title_zh"]
                            elif "abstract" in paper_details["data"][0]:
                                paper_desc = paper_details["data"][0]["abstract"]
                            elif "title" in paper_details["data"][0]:
                                paper_desc = paper_details["data"][0]["title"]
                                
                            
                            before_cite = gathered_tmp_text[:gathered_tmp_text.index(cite)].split("。")
                            after_cite = gathered_tmp_text[gathered_tmp_text.index(cite) + len(cite):].split("。")
                            
                            before_context = before_cite[-1] if before_cite else ""
                            after_context = after_cite[0] if after_cite else ""
                            
                            cite_context = before_context + after_context
                            
                            tmp_prompt = """请判断tag: abstract与tag: context的内容之间的技术与领域相关性, 并直接返回一个相关性得分(属于0到100的正整数), 如果两个内容是强相关则是100分, 如果两个内容完全无关则认为是0分. 
                            无需任何解释或说明. 你认为abstract与context的内容相关性得分为:
                            """
                            tmp_response = query_qwen_plus(f"<abstract>{paper_desc}<abstract>\n<context>{cite_context}<context>" + tmp_prompt)
                            # 使用正则表达式提取相关性得分
                            
                            score_match = re.search(r'\b([0-9]|[1-9][0-9]|100)\b', tmp_response)
                            relevance_score = int(score_match.group(1)) if score_match else 0
                            
                            # 根据相关性得分决定是否添加该引用
                            if relevance_score >= 60:
                                cite_str = generate_citation(paper_details["data"][0])
                                index_+=1
                                if cite in replace_dict:
                                    replace_dict[cite].append((index_, cite_str))
                                else:
                                    replace_dict[cite] = [(index_, cite_str)]
                                paper_details["index"] = index_
                                bib_container.append(paper_details)
            else:
                # 未检索到有效数据.
                pass
    
    with open('./output/bib_container_from_pipelineC2.json', 'w', encoding='utf-8') as f:
        json.dump(bib_container, f, ensure_ascii=False, indent=4)
    
    # 获取最后的引用文献列表.
    final_bib_list = generate_bibliography(bib_container)
    
    # 论文表去重, 并生成前<->后序号的mapping字典.
    deduplicated_list, mapping_dict = deduplicate_references(final_bib_list)

    # 将全文通用信息存出去.
    with open('./output/deduplicated_list_from_pipelineC2.json', 'w', encoding='utf-8') as f:
        json.dump([d[1] for d in deduplicated_list], f, ensure_ascii=False, indent=4)
    
    # 重构序号格式.
    new_replace_dict = {}
    for key_ in replace_dict:
        tuplesList = replace_dict[key_]
        new_tuplesList = []
        for tuple_ in tuplesList:
            tuple_0 = mapping_dict[tuple_[0]]
            tuple_1 = tuple_[1]
            new_tuple = (tuple_0, tuple_1)
            if new_tuple not in new_tuplesList:
                new_tuplesList.append(new_tuple)
        new_str_head = ""
        new_str_tail = "（"
        for new_tuple in new_tuplesList:
            new_str_head += f"[{new_tuple[0]}]"
            new_str_tail += f"{new_tuple[1]}；"
        new_str_tail= new_str_tail[:-1] + "）"
        new_replace_dict[key_] = new_str_head+new_str_tail
        
    for cite in citations:
        if cite in new_replace_dict:
            substitution = new_replace_dict[cite]
        else:
            substitution = ""
        # 替换引用格式
        # [可改] 引用格式在此重写.
        gathered_tmp_text = gathered_tmp_text.replace(cite, substitution)

    # 添加markdown目录大标题
    bib_gathered_str = "# **文献目录**\n"
    for tuple_ in deduplicated_list:
        bib_gathered_str += f"[{tuple_[0]}] {tuple_[1]}\n"
        
    converter = MarkdownToDocxConverter()
    converter.convert(gathered_tmp_text+bib_gathered_str, output_path)

    
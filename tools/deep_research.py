import json
from api.qwen_72b import query_qwen_72b
from utils.chapter1_utils import extract_json_from_string, generate_8char_md5
from tqdm import tqdm
from api.tavily_normal import query_zhihu
from api.serper_normal import query_singleWebsite

def search_zhihu(paper_title, paragraph_title, paragraph_task, basic_info, max_retrieval4eachKeyword = 2):
    # 查询知乎
    tmp_prompt_1 = f"""
    tag: basic_info中的内容为当前论文的基本信息概况.
    当前我需要构建标题为"{paper_title}"的论文章节"{paragraph_title}"的相关内容, {paragraph_task}
    请结合我上述的基本信息与需求描述, 为我提供2个在知乎上查找资料时所使用的关键字.
    请以一个json-list的格式将答案提供给我, 
    回复请以```json开头, 以```结尾, 无需添加任何多余解释和说明.
    """
    tmp_response_1 = query_qwen_72b(f"<basic_info>{basic_info}<basic_info>\n" + tmp_prompt_1)
    # print("知乎关键字:", paragraph_title, tmp_response_1)
        
    keywordsList = extract_json_from_string(tmp_response_1)
    zhihu_list = []
    
    for keyword in tqdm(keywordsList):
        try:
            zhihu_linksList = query_zhihu(keyword, threshold=0.618)
        except Exception as e:
            print("[deep_research] #1", e)
            continue
        tmp_prompt_2 = f"""
        tag: markdown中的内容为一个与"{keyword}"相关的知乎页面原文.
        请为我从上述原文中, 梳理出干净的纯文本页面内容, 无需添加其他解释说明.
        只需要保留原文中的主要内容与逻辑关系, 以及所涉及的各个技术点的描述与细节.
        剔除诸如页面功能与其他栏目等无关内容.
        """
        
        for zhihu_link in zhihu_linksList[:max_retrieval4eachKeyword]:
            tmp_page = query_singleWebsite(zhihu_link)
            try:
                tmp_markdown = tmp_page["markdown"]
            except Exception as e:
                print(e, tmp_markdown)
                continue
            # 近一步用qwen_72b来清洗页面内容.
            try:
                tmp_response_2 = query_qwen_72b(f"<markdown>{tmp_markdown}<markdown>\n" + tmp_prompt_2, model = "qwen2.5-72b-instruct")
            except Exception as e:
                # print(e)
                md5_value = generate_8char_md5(zhihu_link)
                badcase_filepath = f"./badcases/{keyword}_{md5_value}.txt"
                with open(badcase_filepath, "w") as f:
                    f.write(f"<markdown>{tmp_markdown}<markdown>\n{tmp_prompt_2}")
                    print({"keyword": keyword, "zhihu_link": zhihu_link}, "拉取失败, 文件已储存至", badcase_filepath)
                continue
            zhihu_list.append({"keyword": keyword, "zhihu_link": zhihu_link, "content": tmp_response_2})
            # print("结束一个了, 开心!")
            
    with open("./output/zhihu_list_from_pipelineC1.json", "a", encoding='utf-8') as f:
        for zhihu_element in zhihu_list:
            tmp_zhihu_element = zhihu_element.copy()
            tmp_zhihu_element["paragraph_title"] = paragraph_title
            f.write(json.dumps(tmp_zhihu_element, ensure_ascii=False, indent=None)+"\n")
    return zhihu_list
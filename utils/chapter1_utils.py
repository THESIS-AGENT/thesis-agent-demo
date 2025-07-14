import re
import json
import hashlib

def extract_content_between_triple_dollars(text):
    """
    提取字符串中$$$...$$$之间的内容
    
    参数:
        text (str): 输入的字符串，如 "1.2.1 $$$论文领域大方向$$$研究现状"
        
    返回:
        str: $$$...$$$之间的内容，如果没有找到则返回None
    """
    import re
    
    # 使用正则表达式匹配$$$...$$$之间的内容
    pattern = r'\${3}(.*?)\${3}'
    match = re.search(pattern, text)
    
    # 如果找到匹配，则返回匹配到的内容
    if match:
        return match.group(1)
    else:
        return None
    

def extract_json_from_string(text):
    """
    从文本中提取JSON内容
    
    Args:
        text (str): 包含JSON的字符串，可能被```json和```包围
        
    Returns:
        dict or list: 解析后的JSON对象
        
    Raises:
        json.JSONDecodeError: 如果无法解析JSON
    """
    # 使用正则表达式匹配```json 和 ```之间的内容
    pattern = r'```json\s*([\s\S]*?)\s*```'
    match = re.search(pattern, text)
    
    if match:
        # 提取匹配到的JSON字符串内容
        json_str = match.group(1)
        # 解析JSON
        return json.loads(json_str)
    else:
        # 如果没有匹配到Markdown格式的JSON，尝试直接解析整个字符串
        return json.loads(text)
    

def generate_8char_md5(input_str):
    """
    将输入字符串转换为8位MD5哈希值
    
    参数:
        input_str: 输入字符串
    
    返回:
        8位MD5哈希值字符串
    """
    # 确保输入是字符串类型
    if not isinstance(input_str, str):
        input_str = str(input_str)
    
    # 将字符串编码为bytes对象
    input_bytes = input_str.encode('utf-8')
    
    # 计算MD5哈希值
    md5_hash = hashlib.md5(input_bytes).hexdigest()
    
    # 返回前8位
    return md5_hash


def get_truncated_tmp_list(tmp_list, threshold=16666):
    """
    随机打乱列表并返回满足字符串长度阈值的子列表
    
    Args:
        tmp_list (list): 原始列表
        threshold (int): 字符串长度阈值，默认5000
        
    Returns:
        list: 处理后的列表
    """
    import random
    import json
    
    # 创建原列表的副本并打乱
    shuffled_list = tmp_list.copy()
    random.shuffle(shuffled_list)
    
    # 二分查找合适的列表长度
    left, right = 1, len(shuffled_list)
    result = []
    
    while left <= right:
        mid = (left + right) // 2
        current_list = shuffled_list[:mid]
        current_length = len(json.dumps(current_list, ensure_ascii=False))
        
        if current_length <= threshold:
            result = current_list
            left = mid + 1
        else:
            right = mid - 1
    
    return result


def extract_content_between_triple_dollars(text):
    """
    提取字符串中$$$...$$$之间的内容
    参数:
        text (str): 输入的字符串，如 "1.2.1 $$$论文领域大方向$$$研究现状"
    返回:
        str: $$$...$$$之间的内容，如果没有找到则返回None
    """
    import re
    
    # 使用正则表达式匹配$$$...$$$之间的内容
    pattern = r'\${3}(.*?)\${3}'
    match = re.search(pattern, text)
    
    return match.group(1)


from api.qwen_72b import query_qwen_72b
def get_new_title(title, basic_info):
    tmp_prompt_4 = """
    tag: basic_info的内容为当前论文的基本信息.
    请为我从论文的基本信息中, 挖掘出"{}",
    你只需要返回最精准最简短的一个目标内容即可, 无需添加任何解释说明或格式.
    """
    target_part = extract_content_between_triple_dollars(title)
    tmp_prompt_inner = tmp_prompt_4.format(target_part)
    generated_part = query_qwen_72b(f"<basic_info>{basic_info}<basic_info>\n"+ tmp_prompt_inner)
    return title.replace("$$$" + target_part + "$$$", generated_part)


from utils.global_template_utils import extract_feedback_for_general_purpose
def check_title(title, basic_info):
    tmp_prompt_5 = """
    tag: basic_info的内容为当前论文的基本信息.
    当前工作流正在构建的论文章节名称为"{}",
    你需要判断这个章节名是否合理, 若合理, 则直接返回true; 若不合理(例如出现冗余内容, 不通顺的内容或重复性内容), 则直接返回包含原章节编号的新名字.
    """
    tmp_prompt_inner = tmp_prompt_5.format(title)
    generated_part = query_qwen_72b(f"<basic_info>{basic_info}<basic_info>\n"+ tmp_prompt_inner)
    result_ = extract_feedback_for_general_purpose(generated_part)
    return title if result_ is True else result_


def get_truncated_zhihu_list(zhihu_list, threshold=13333):
    """
    随机打乱列表并返回满足字符串长度阈值的子列表
    
    Args:
        tmp_list (list): 原始列表
        threshold (int): 字符串长度阈值
        
    Returns:
        list: 处理后的列表
    """
    import random
    import json
    
    # 创建原列表的副本并打乱
    shuffled_list = zhihu_list.copy()
    random.shuffle(shuffled_list)
    
    # 二分查找合适的列表长度
    left, right = 1, len(shuffled_list)
    result = []
    
    while left <= right:
        mid = (left + right) // 2
        current_list = shuffled_list[:mid]
        current_length = len(json.dumps(current_list, ensure_ascii=False))
        
        if current_length <= threshold:
            result = current_list
            left = mid + 1
        else:
            right = mid - 1
    
    return result

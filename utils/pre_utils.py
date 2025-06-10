import json
import re

def extract_and_validate_json(text):
    """
    从文本中提取JSON并验证其格式
    
    参数:
        text: 包含JSON的文本字符串，可能被```json和```包围
        
    返回:
        如果JSON格式正确（list中每个dict都包含content和feedback字段）,
        则返回格式化后的JSON字符串；否则返回去除```json和```后的原始文本
    """
    
    # 使用正则表达式从文本中提取JSON部分
    json_pattern = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(json_pattern, text)
    
    if not match:
        # 如果没有找到```json包裹的内容，直接返回原文本
        return text
    
    # 提取JSON文本内容
    json_text = match.group(1).strip()
    
    try:
        # 尝试解析JSON
        json_data = json.loads(json_text)
        
        # 验证JSON结构：必须是列表，且每个元素都是包含content和feedback字段的字典
        if not isinstance(json_data, list):
            # 如果不是列表，返回去除标记的原始JSON文本
            return json_text
        
        # 检查每个元素是否都是字典且包含必要字段
        for item in json_data:
            if not isinstance(item, dict) or "content" not in item or "feedback" not in item:
                # 如果有任何元素不符合要求，返回去除标记的原始JSON文本
                return json_text
        
        # 验证通过，返回格式化的JSON
        return json.dumps(json_data, ensure_ascii=False, indent=4)
    
    except json.JSONDecodeError:
        # JSON解析错误，返回去除标记的原始文本
        return json_text
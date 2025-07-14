import re

def get_part_two_template(file_path):
    # 使用 locals 字典来存储执行后的局部变量
    local_vars = {}
    file_name = file_path.split("/")[-1]
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 执行文件内容，将变量存储在 local_vars 中
        exec(file_content, {}, local_vars)
        
        # 从局部变量中获取 part_two_template
        if 'part_two_template' in local_vars:
            return local_vars['part_two_template']
        else:
            return f"在文件'{file_name}'中未找到 part_two_template 变量"

    except Exception as e:
        return f"读取模板文件'{file_name}'时出错: {str(e)}"


def validate_part_two_template(template):
    # 检查顶层结构
    if not isinstance(template, dict) or 'content' not in template:
        return False, "错误: 顶层结构必须是包含 'content' 键的字典"
    
    if not isinstance(template['content'], list) or len(template['content']) == 0:
        return False, "错误: 'content' 必须是非空列表"
    
    # 检查章级结构
    chapter = template['content'][0]
    required_chapter_keys = ['段落名', '段落描述', 'content']
    if not all(key in chapter for key in required_chapter_keys):
        return False, f"错误: 章级结构缺少必要字段: {required_chapter_keys}"
    
    if not isinstance(chapter['content'], list):
        return False, "错误: 章级 'content' 必须是列表"
    
    # 递归检查子段落结构
    def validate_section(section):
        # 检查必要字段
        if '段落名' not in section or '段落描述' not in section:
            return False
        
        # 如果有 content 字段，检查其结构
        if 'content' in section:
            if not isinstance(section['content'], list):
                return False
            
            # 递归检查每个子段落
            for subsection in section['content']:
                if not validate_section(subsection):
                    return False
        
        return True

    # 检查所有节级段落
    for section in chapter['content']:
        if not validate_section(section):
            return False, f"错误: 子段落结构缺少必要字段 '段落名' 或 '段落描述'; 且子段落结构 '{section['段落名']}' 的 'content' 必须是列表"
    
    # 所有检查都通过
    return True


def extract_citations(content):
    """
    从文件中提取所有<citation>...</citation>标记的内容，并按原文出现顺序放入列表
    
    Args:
        content: 待处理文本
        
    Returns:
        包含所有引用内容的列表
    """
    try:
        # 使用正则表达式匹配所有<citation>...</citation>内容
        citation_pattern = r'<citation>.*?</citation>'
        citations = re.findall(citation_pattern, content, re.DOTALL)
        
        return citations
    except Exception as e:
        print(f"[extract_citations] 处理文件时出错: {e}")
        return []
    

def generate_citation(paper_data):
    """
    Generate a citation string from paper data.
    Format: (作者1等人, 年份) or (作者1, 作者2, 年份) if fewer than 3 authors
    Returns empty string if no authors and no year.
    """
    if not paper_data:
        return ""
    
    # Extract authors - check for both Chinese and English versions
    authors = []
    if "authors" in paper_data and paper_data["authors"]:
        for author in paper_data["authors"]:
            if "name_zh" in author and author["name_zh"]:
                authors.append(author["name_zh"])
            elif "name" in author and author["name"]:
                authors.append(author["name"])
    
    # Extract year
    year = ""
    if "year" in paper_data and paper_data["year"]:
        year = str(paper_data["year"]) + "年"
    
    # Format citation based on number of authors
    if not authors and not year:
        return ""
    
    citation = ""
    if authors:
        if len(authors) >= 3:
            citation += f"{authors[0]}等人"
        else:
            citation += "，".join(authors)
    
    if authors and year:
        citation += "，"
    
    citation += year
    
    return citation


def generate_bibliography(json_list):
    """
    从JSON列表中生成标准格式的参考文献列表
    """
    bibliography = []
    
    for index, item in enumerate(json_list, 1):
        # 获取论文数据
        paper_data = None
        if 'data' in item and item['data'] and len(item['data']) > 0:
            paper_data = item['data'][0]
        else:
            continue
        
        # 构建标题 (优先使用中文标题)
        title = paper_data.get('title_zh', '') or paper_data.get('title', '')
        if not title:
            continue
            
        # 构建作者列表
        authors = []
        if 'authors' in paper_data and paper_data['authors']:
            for author in paper_data['authors']:
                # 优先使用中文名
                author_name = author.get('name_zh', '') or author.get('name', '')
                if author_name:
                    authors.append(author_name)
        
        author_str = ""
        if len(authors) > 3:
            # 超过3个作者使用"等"
            author_str = ", ".join(authors[:3]) + "等人"
        else:
            author_str = ", ".join(authors)
            
        # 获取年份
        year = paper_data.get('year', '')
        
        # 获取卷号和期号
        volume = paper_data.get('volume', '')
        issue = paper_data.get('issue', '')
        
        # 获取期刊名称
        venue = ""
        if 'venue' in paper_data and paper_data['venue']:
            venue = paper_data['venue'].get('raw', '')
        
        # 页码信息 (示例数据中没有，使用占位符)
        pages = ""
        
        # 构建参考文献条目
        
        entry = f"{author_str}. {title}"
        
        # 确定文献类型 (期刊[J]还是会议[C])
        pub_type = "[J]"  # 默认为期刊
        
        # 构建文献后续部分
        if venue:
            entry += f"{pub_type} {venue}"
            if year:
                entry += f", {year}"
            if volume:
                entry += f", {volume}"
                if issue:
                    entry += f"({issue})"
            if pages:
                entry += f": {pages}"
            else:
                entry += "."
        elif year:
            entry += f". {year}."
        else:
            entry += "."
            
        bibliography.append((index, entry))
    
    return bibliography

def deduplicate_references(reference_list):
    """
    对参考文献列表进行去重，保持序号连续且升序
    
    参数:
        reference_list: 包含(序号, 文献内容)元组的列表
    
    返回:
        deduplicated_list: 去重后的参考文献列表
        mapping: 原序号到新序号的映射字典
    """
    # 提取文献内容，忽略序号
    contents = [ref[1] for ref in reference_list]
    
    # 创建新的不重复列表
    unique_contents = []
    seen_contents = set()
    
    for content in contents:
        if content not in seen_contents:
            unique_contents.append(content)
            seen_contents.add(content)
    
    # 创建原序号到新序号的映射
    mapping = {}
    for old_index, content in reference_list:
        # 找到内容在唯一内容列表中的位置，加1得到新序号
        new_index = unique_contents.index(content) + 1
        mapping[old_index] = new_index
    
    # 创建去重后的参考文献列表，新序号连续且升序
    deduplicated_list = [(i+1, content) for i, content in enumerate(unique_contents)]
    
    return deduplicated_list, mapping

def clean_template(template):
    """
    清理模板中的 if_tech 和 if_lag 字段，只保留段落名、段落描述和content字段
    
    Args:
        template (dict): 原始模板字典
    
    Returns:
        dict: 清理后的模板字典
    """
    def clean_node(node):
        # 创建新的字典，只包含需要的字段
        cleaned = {}
        
        if "段落名" in node:
            cleaned["段落名"] = node["段落名"]
        if "段落描述" in node:
            cleaned["段落描述"] = node["段落描述"]
        if "content" in node:
            cleaned["content"] = [clean_node(item) for item in node["content"]]
            
        return cleaned
    
    # 对整个模板进行清理
    return {
        "content": [clean_node(section) for section in template["content"]]
    }
    
def remove_python_flag(input_python_code_snippet):
    return input_python_code_snippet.replace("```python", "").replace("```", "")
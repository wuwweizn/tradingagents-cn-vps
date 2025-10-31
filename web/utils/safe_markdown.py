"""
安全的Markdown渲染工具
用于避免移动浏览器中的正则表达式解析错误
"""

import streamlit as st
import re
import html


def safe_markdown(text: str):
    """
    安全地渲染Markdown内容，避免手机浏览器中的正则表达式错误
    
    这个方法使用HTML渲染方式，完全避免Streamlit的GFM自动链接功能
    从而避免正则表达式解析错误
    
    Args:
        text: 要渲染的文本内容
    
    Returns:
        无返回值，直接渲染到Streamlit界面
    """
    if not text:
        return
    
    # 完全转义HTML特殊字符
    escaped = html.escape(text)
    
    # 将换行符转换为HTML换行
    escaped = escaped.replace('\n', '<br>')
    
    # 处理Markdown基本语法，转换为HTML
    # 标题 (只处理一级到三级标题，避免过度解析)
    escaped = re.sub(r'^###\s+(.+?)$', r'<h3>\1</h3>', escaped, flags=re.MULTILINE)
    escaped = re.sub(r'^##\s+(.+?)$', r'<h2>\1</h2>', escaped, flags=re.MULTILINE)
    escaped = re.sub(r'^#\s+(.+?)$', r'<h1>\1</h1>', escaped, flags=re.MULTILINE)
    
    # 粗体和斜体（需要小心处理，避免嵌套问题）
    # 先处理粗体
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
    # 再处理斜体（避免与粗体冲突）
    escaped = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', escaped)
    
    # 处理代码（行内代码）
    escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
    
    # 处理列表（简单的无序列表）
    lines = escaped.split('<br>')
    processed_lines = []
    in_list = False
    
    for line in lines:
        # 检测列表项
        if re.match(r'^\s*[-*+]\s+', line):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            # 移除列表标记并提取内容
            content = re.sub(r'^\s*[-*+]\s+', '', line)
            processed_lines.append(f'<li>{content}</li>')
        elif re.match(r'^\s*\d+\.\s+', line):
            if not in_list:
                processed_lines.append('<ol>')
                in_list = True
            content = re.sub(r'^\s*\d+\.\s+', '', line)
            processed_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>' if not any('<ol>' in l for l in processed_lines[-10:]) else '</ol>')
                in_list = False
            processed_lines.append(line)
    
    if in_list:
        processed_lines.append('</ul>')
    
    escaped = '<br>'.join(processed_lines)
    
    # 使用HTML渲染，避免Markdown解析器的自动链接功能
    st.markdown(escaped, unsafe_allow_html=True)


def safe_markdown_simple(text: str):
    """
    简单的安全渲染方法
    只转义特殊字符，保留基本文本格式
    """
    if not text:
        return
    
    # 直接使用st.write，完全避免Markdown解析
    # 但保留换行和基本格式
    text = text.replace('\n', '  \n')  # Markdown的双空格换行
    st.markdown(text, unsafe_allow_html=False)


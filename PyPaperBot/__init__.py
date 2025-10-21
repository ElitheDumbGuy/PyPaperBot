# 文件: /Users/narra/Documents/alib/Writer/.pytools/paper-bot/src/PyPaperBot/__init__.py

__version__ = "1.4.1"

import os
import re
import io

try:
    import pandas as pd
    import markdown
except ImportError:
    print("PyPaperBot: 'pandas' and 'markdown' libraries are required for Markdown parsing.")
    print("Please run: pip install pandas markdown")

from .Scholar import ScholarPapersInfo
from .Downloader import downloadPapers


def download_paper_by_title(title: str, download_dir: str, headless: bool = True) -> (str | None):
    """
    通过文献标题搜索并下载 PDF。

    此函数封装了使用 Selenium 搜索 Google Scholar、获取第一个结果、
    然后尝试从 Sci-Hub 或 Anna's Archive 下载的完整流程。

    Args:
        title (str): 要搜索的文献标题。
        download_dir (str): 保存 PDF 的目录路径。
        headless (bool, optional): 是否以无头模式运行 Chrome。
                                   调试时可设置为 False。默认为 True。

    Returns:
        str | None: 如果成功，返回下载的 PDF 文件的完整路径；否则返回 None。
    """

    print(f"[PyPaperBot] 任务开始: 搜索 '{title}'")

    # 1. 确保目录存在
    try:
        os.makedirs(download_dir, exist_ok=True)
    except Exception as e:
        print(f"[PyPaperBot] 错误: 无法创建下载目录: {download_dir}. 错误: {e}")
        return None

    # 2. 搜索论文 (使用我们调试好的半自动Selenium逻辑)
    papers_list = []
    try:
        print("[PyPaperBot] 正在使用 Selenium (半自动模式) 搜索 Google Scholar...")
        papers_list = ScholarPapersInfo(
            query=title,
            scholar_pages=range(1, 2),  # 仅第1页
            restrict=None,  # 获取所有元数据
            scholar_results=1,  # 仅第1个结果
            chrome_version=True,  # 触发半自动逻辑
            headless=headless  # 传递 headless 标志
        )
    except Exception as e:
        print(f"[PyPaperBot] 错误: Scholar 搜索失败: {e}")
        return None

    if not papers_list:
        print(f"[PyPaperBot] 警告: 未在 Scholar 上找到标题为 '{title}' 的结果")
        return None

    paper_object = papers_list[0]
    print(f"[PyPaperBot] 找到论文: '{paper_object.title}' (DOI: {paper_object.DOI})")

    # 3. 覆盖文件名
    # 强制使用用户提供的 *输入* 标题作为文件名
    # 这样 getFileName() 将使用我们想要的名称
    paper_object.title = title
    paper_object.use_doi_as_filename = False  # 确保它使用标题

    # 4. 下载
    try:
        print(f"[PyPaperBot] 正在尝试从 Sci-Hub/Anna's Archive 下载...")
        downloadPapers(
            [paper_object],
            download_dir,
            num_limit=None,
            SciHub_URL=None,
            SciDB_URL=None
        )
    except Exception as e:
        print(f"[PyPaperBot] 错误: 下载失败: {e}")
        return None

    # 5. 验证并返回路径
    if paper_object.downloaded:
        # 我们必须手动找到文件，因为 downloadPapers 不返回路径
        # 并且 getSaveDir 可能会添加 (2), (3) 等前缀

        # 这是 Paper.py 中的文件名清理逻辑
        base_name = re.sub(r'[^\w\-_. ]', '_', title)
        found_path = None

        try:
            for fname in os.listdir(download_dir):
                # 检查是否是 PDF 并且包含我们清理后的基础名称
                if fname.lower().endswith(".pdf") and base_name in fname:
                    found_path = os.path.join(download_dir, fname)
                    break  # 找到第一个匹配项
        except Exception as e:
            print(f"[PyPaperBot] 错误: 验证文件时出错: {e}")
            return None

        if found_path:
            print(f"[PyPaperBot] 成功! 下载到: {found_path}")
            return found_path
        else:
            # 这种情况很奇怪：下载报告成功，但我们找不到它
            print(f"[PyPaperBot] 错误: 下载报告成功，但在 {download_dir} 中找不到匹配的文件。")
            return None
    else:
        print(f"[PyPaperBot] 错误: 论文 '{title}' 下载失败。")
        return None


# ----- !!! 新增函数从这里开始 !!! -----

def download_papers_from_markdown(markdown_file_path: str, download_dir: str, headless: bool = True) -> dict:
    """
    从 Markdown 文件中读取所有表格，提取 "标题" 列，并下载所有论文。

    Args:
        markdown_file_path (str): .md 文件的完整路径。
        download_dir (str): 保存所有 PDF 的目录路径。
        headless (bool, optional): 是否以无头模式运行 Chrome。默认为 True。

    Returns:
        dict: 一个字典，键是论文标题，值是下载路径 (如果成功) 或 None (如果失败)。
    """

    print(f"[PyPaperBot] --- 开始 Markdown 批量下载任务 ---")

    # --- 1. 检查依赖 ---
    try:
        pd
        markdown
    except NameError:
        print("[PyPaperBot] 错误: 'pandas' 和 'markdown' 库未安装。")
        print("请运行: pip install pandas markdown")
        return {}

    # --- 2. 读取 Markdown 文件 ---
    if not os.path.exists(markdown_file_path):
        print(f"[PyPaperBot] 错误: 找不到 Markdown 文件: {markdown_file_path}")
        return {}

    print(f"[PyPaperBot] 正在读取: {markdown_file_path}")
    md_content = ""
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except Exception as e:
        print(f"[PyPaperBot] 错误: 读取文件失败: {e}")
        return {}

    # --- 3. 解析 Markdown -> HTML -> DataFrames ---
    try:
        html_string = markdown.markdown(md_content, extensions=['tables'])
        all_dataframes = pd.read_html(io.StringIO(html_string))
    except Exception as e:
        print(f"[PyPaperBot] 错误: 解析 Markdown 表格失败: {e}")
        return {}

    if not all_dataframes:
        print("[PyPaperBot] 警告: 在 Markdown 文件中未找到任何表格。")
        return {}

    print(f"[PyPaperBot] 成功解析 {len(all_dataframes)} 个表格。")

    # --- 4. 提取所有标题 ---
    titles_to_download = []
    seen_titles = set()
    possible_columns = ["标题", "Title", "title", "文献标题", "篇名"]  # 可能的列名

    for i, df in enumerate(all_dataframes):
        title_col = None
        for col in possible_columns:
            if col in df.columns:
                title_col = col
                break

        if title_col:
            print(f"[PyPaperBot] 正在从表格 {i + 1} (列: '{title_col}') 读取标题...")
            for title in df[title_col]:
                # 确保标题是有效的字符串 (非 NaN, None, etc.)
                if isinstance(title, str) and title.strip():
                    cleaned_title = title.strip()
                    if cleaned_title not in seen_titles:
                        titles_to_download.append(cleaned_title)
                        seen_titles.add(cleaned_title)
        else:
            print(f"[PyPaperBot] 警告: 表格 {i + 1} 中未找到 '标题' 列，跳过。")

    if not titles_to_download:
        print("[PyPaperBot] 错误: 在所有表格中均未找到有效的论文标题。")
        return {}

    print(f"[PyPaperBot] --- 共找到 {len(titles_to_download)} 个唯一标题。开始下载... ---")

    # --- 5. 循环下载 ---
    download_results = {}
    for i, title in enumerate(titles_to_download):
        print(f"\n[PyPaperBot] 正在处理: {i + 1} / {len(titles_to_download)}")
        file_path = download_paper_by_title(title, download_dir, headless)
        download_results[title] = file_path
        print("-" * 30)  # 添加分隔符

    # --- 6. 返回总结 ---
    success_count = sum(1 for p in download_results.values() if p)
    print(f"[PyPaperBot] --- Markdown 批量下载任务完成 ---")
    print(f"成功下载: {success_count} / {len(download_results)}")

    return download_results
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 11:59:42 2020

@author: Vito
"""
import time
import requests
import functools
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from .HTMLparsers import schoolarParser
from .Crossref import getPapersInfo
from .NetInfo import NetInfo

# --- 新增导入 ---
import os
import re
import subprocess


# --- 结束新增 ---


def waithIPchange():
    while True:
        inp = input('You have been blocked, try changing your IP or using a VPN. '
                    'Press Enter to continue downloading, or type "exit" to stop and exit....')
        if inp.strip().lower() == "exit":
            return False
        elif not inp.strip():
            print("Wait 30 seconds...")
            time.sleep(30)
            return True


# ----- 核心修改 1: 添加 headless=True 参数 -----
def scholar_requests(scholar_pages, url, restrict, chrome_version, scholar_results=10, headless=True):
    javascript_error = "Sorry, we can't verify that you're not a robot when JavaScript is turned off"
    to_download = []
    driver = None

    # ... ("半自动" 方案的检测逻辑保持不变) ...
    # ... (从 "detected_version = None" 到 "chrome_version = None # 退回到 requests") ...
    detected_version = None
    CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if chrome_version is not None:
        if not os.path.exists(CHROME_BINARY_PATH):
            print(f"!!! Selenium 错误: Chrome 路径未找到: {CHROME_BINARY_PATH}")
            print("请安装 Chrome 浏览器或在 Scholar.py 中更正路径。")
            chrome_version = None
        else:
            try:
                command = [CHROME_BINARY_PATH, "--version"]
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                version_string = result.stdout.strip()
                match = re.search(r"(\d+)", version_string)
                if match:
                    detected_version = int(match.group(1))
                    print(f"检测到 Chrome 版本: {detected_version} (路径: {CHROME_BINARY_PATH})")
                else:
                    print(f"无法从 '{version_string}' 中提取版本号。")
                    chrome_version = None
            except Exception as e:
                print(f"自动检测 Chrome 版本时出错: {e}")
                chrome_version = None
                # ... (检测逻辑结束) ...

    for i in scholar_pages:
        while True:
            res_url = url % (scholar_results * (i - 1))

            if chrome_version is not None and detected_version is not None:
                if driver is None:
                    print(f"Using Selenium driver (半自动模式, Headless={headless})")

                    driver = uc.Chrome(
                        headless=headless,
                        use_subprocess=False,
                        binary_location=CHROME_BINARY_PATH,
                        version_main=detected_version
                    )

                driver.get(res_url)

                # ----- ！！！新增的等待！！！ -----
                # Google Scholar 严重依赖 JS 来加载结果。
                # driver.get() 立即返回，但此时页面可能还是空的。
                # 我们添加一个短暂的硬编码等待，让 JS 有时间运行。
                wait_time = 3  # 3 秒
                print(f"Waiting {wait_time} seconds for Google Scholar JavaScript to load results...")
                time.sleep(wait_time)
                # ---------------------------------

                html = driver.page_source  # 现在才抓取 HTML

                # ----- ！！！新增的调试转储！！！ -----
                debug_file = "debug_scholar_page.html"
                try:
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"!!! 已将调试HTML转储到: {os.path.abspath(debug_file)}")
                except Exception as e:
                    print(f"!!! 无法写入调试文件: {e}")
                # ------------------------------------

            else:
                if chrome_version is not None and detected_version is None:
                    print("Selenium 启动失败 (未检测到版本)，退回到 'requests' 模式。")
                    chrome_version = None

                html = requests.get(res_url, headers=NetInfo.HEADERS)
                html = html.text

            if javascript_error in html:
                # ... (此块保持不变) ...
                is_continue = waithIPchange()
                if not is_continue:
                    return to_download
            else:
                break

        papers = schoolarParser(html)
        # ... (函数的其余部分保持不变) ...
        if len(papers) > scholar_results:
            papers = papers[0:scholar_results]

        print("\nGoogle Scholar page {} : {} papers found".format(i, scholar_results))

        if len(papers) > 0:
            papersInfo = getPapersInfo(papers, url, restrict, scholar_results)
            info_valids = functools.reduce(lambda a, b: a + 1 if b.DOI is not None else a, papersInfo, 0)
            print("Papers found on Crossref: {}/{}\n".format(info_valids, len(papers)))

            to_download.append(papersInfo)
        else:
            print("Paper not found...")

    return to_download


def parseSkipList(skip_words):
    skip_list = skip_words.split(",")
    print("Skipping results containing {}".format(skip_list))
    output_param = ""
    for skip_word in skip_list:
        skip_word = skip_word.strip()
        if " " in skip_word:
            output_param += '+-"' + skip_word + '"'
        else:
            output_param += '+-' + skip_word
    return output_param


# ----- 核心修改 3: 添加 headless=True 参数 -----
def ScholarPapersInfo(query, scholar_pages, restrict, min_date=None, scholar_results=10, chrome_version=None,
                      cites=None, skip_words=None, headless=True):
    url = r"https://scholar.google.com/scholar?hl=en&as_vis=1&as_sdt=1,5&start=%d"
    if query:
        if len(query) > 7 and (query.startswith("http://") or query.startswith("https://")):
            url = query
        else:
            url += f"&q={query}"
        if skip_words:
            url += parseSkipList(skip_words)
            print(url)
    if cites:
        url += f"&cites={cites}"
    if min_date:
        url += f"&as_ylo={min_date}"

    # ----- 核心修改 4: 传递 headless 参数 -----
    to_download = scholar_requests(scholar_pages, url, restrict, chrome_version, scholar_results, headless=headless)

    return [item for sublist in to_download for item in sublist]
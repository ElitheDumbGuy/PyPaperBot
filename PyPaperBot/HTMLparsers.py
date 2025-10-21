# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 11:59:42 2020

@author: Vito
"""
from bs4 import BeautifulSoup
import re


def schoolarParser(html):
    result = []
    soup = BeautifulSoup(html, "html.parser")

    # ----- 核心修改 -----
    #
    # 旧的查找器 (过于严格):
    # for element in soup.findAll("div", class_="gs_r gs_or gs_scl"):
    #
    # 新的查找器 (使用 CSS 选择器):
    # 这会找到所有同时包含 .gs_r, .gs_or, 和 .gs_scl 类的 <div> 标签,
    # 无论它们是否还包含其他类 (比如 .gs_fmar)。
    #
    for element in soup.select("div.gs_r.gs_or.gs_scl"):
        # ----- 结束修改 -----

        if not isBook(element):
            title = None
            link = None
            link_pdf = None
            cites = None
            year = None
            authors = None
            for h3 in element.findAll("h3", class_="gs_rt"):  # findAll在这里没问题
                found = False
                for a in h3.findAll("a"):
                    if not found:
                        title = a.text
                        link = a.get("href")
                        found = True
            for a in element.findAll("a"):
                if "Cited by" in a.text:
                    try:  # 增加一个 try-except 避免 "Cited by" 后面不是数字时崩溃
                        cites = int(a.text[8:])
                    except ValueError:
                        cites = None
                if "[PDF]" in a.text:
                    link_pdf = a.get("href")
            for div in element.findAll("div", class_="gs_a"):
                try:
                    authors, source_and_year, source = div.text.replace('\u00A0', ' ').split(" - ")
                except ValueError:
                    continue

                if not authors.strip().endswith('\u2026'):
                    # There is no ellipsis at the end so we know the full list of authors
                    authors = authors.replace(', ', ';')
                else:
                    authors = None
                try:
                    year = int(source_and_year[-4:])
                except ValueError:
                    continue
                if not (1000 <= year <= 3000):
                    year = None
                else:
                    year = str(year)
            if title is not None:
                result.append({
                    'title': title,
                    'link': link,
                    'cites': cites,
                    'link_pdf': link_pdf,
                    'year': year,
                    'authors': authors})
    return result


def isBook(tag):
    result = False
    for span in tag.findAll("span", class_="gs_ct2"):
        if span.text == "[B]":
            result = True
    return result


def getSchiHubPDF(html):
    result = None
    soup = BeautifulSoup(html, "html.parser")

    iframe = soup.find(id='pdf') #scihub logic
    plugin = soup.find(id='plugin') #scihub logic
    download_scidb = soup.find("a", text=lambda text: text and "Download" in text, href=re.compile(r"\.pdf$")) #scidb logic
    embed_scihub = soup.find("embed") #scihub logic

    if iframe is not None:
        result = iframe.get("src")

    if plugin is not None and result is None:
        result = plugin.get("src")

    if result is not None and result[0] != "h":
        result = "https:" + result

    if download_scidb is not None and result is None:
        result = download_scidb.get("href")

    if embed_scihub is not None and result is None:
        result = embed_scihub.get("original-url")

    return result


def SciHubUrls(html):
    result = []
    soup = BeautifulSoup(html, "html.parser")

    for ul in soup.findAll("ul"):
        for a in ul.findAll("a"):
            link = a.get("href")
            if link.startswith("https://sci-hub.") or link.startswith("http://sci-hub."):
                result.append(link)

    return result

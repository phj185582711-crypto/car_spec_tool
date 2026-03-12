# -*- coding: utf-8 -*-
import pdfplumber
from typing import List, Dict


def parse_pdf(pdf_path: str) -> List[Dict]:
    """
    解析PDF，提取文本和位置信息（处理编码问题）
    """
    all_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # 提取文本并强制转UTF-8，避免编码乱码
            raw_text = page.extract_text() or ""
            text = raw_text.encode('utf-8', errors='ignore').decode('utf-8')

            # 提取文字位置信息（用于后续溯源）
            words = page.extract_words()

            page_info = {
                "page_num": page_num,
                "text": text,
                "words": words
            }
            all_pages.append(page_info)

            # 用英文打印，避免中文编码报错
            # print(f"Page {page_num} parsed successfully")

    return all_pages


# 测试代码（可选，注释掉也可以）
if __name__ == "__main__":
    try:
        test_pages = parse_pdf("sample.pdf")
        print(f"Total pages parsed: {len(test_pages)}")
    except Exception as e:
        print(f"Test error: {str(e)}")
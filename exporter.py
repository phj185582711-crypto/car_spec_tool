# -*- coding: utf-8 -*-
import pandas as pd
from typing import List, Dict


def add_source_context(specs: List[Dict], all_pages: List[Dict]) -> List[Dict]:
    """添加原文溯源信息"""
    specs_with_context = []

    for spec in specs:
        page_num = spec.get("page_num", 0)
        spec_name = spec.get("spec_name", "")

        # 找对应页面的文本
        page_text = ""
        for page in all_pages:
            if page["page_num"] == page_num:
                page_text = page["text"]
                break

        # 提取原文片段
        source_context = ""
        if spec_name in page_text:
            idx = page_text.index(spec_name)
            start = max(0, idx - 50)
            end = min(len(page_text), idx + len(spec_name) + 50)
            source_context = page_text[start:end].replace("\n", " ")

        spec_with_context = spec.copy()
        spec_with_context["source_context"] = source_context
        specs_with_context.append(spec_with_context)

    return specs_with_context


def export_to_excel(specs: List[Dict], output_path: str = "extraction_result.xlsx"):
    """导出Excel（英文表头，避免编码问题）"""
    if not specs:
        print("No specifications to export")
        return

    df = pd.DataFrame(specs)

    # 只保留需要的列
    columns = ["page_num", "spec_name", "spec_value", "spec_type", "source_context"]
    columns = [col for col in columns if col in df.columns]
    df = df[columns]

    # 英文表头，避免中文编码问题
    df = df.rename(columns={
        "page_num": "Page Number",
        "spec_name": "Specification Name",
        "spec_value": "Specification Value",
        "spec_type": "Specification Type",
        "source_context": "Source Context"
    })

    # 按页码排序
    df = df.sort_values(by="Page Number")

    # 导出Excel
    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Specifications")

            # 调整列宽
            worksheet = writer.sheets["Specifications"]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"Excel exported successfully to: {output_path}")
    except Exception as e:
        print(f"Excel export failed: {str(e)}")


# 测试代码（可选）
if __name__ == "__main__":
    test_specs = [
        {"page_num": 1, "spec_name": "Low Beam Efficacy", "spec_value": "≥85lm/W", "spec_type": "performance"},
        {"page_num": 2, "spec_name": "Working Temperature Range", "spec_value": "-40℃~105℃", "spec_type": "environment"}
    ]
    test_pages = [
        {"page_num": 1, "text": "Low beam efficacy ≥85lm/W, illumination at 75m ≥20lx", "words": []},
        {"page_num": 2, "text": "Working temperature range -40℃~105℃, meets environmental requirements", "words": []}
    ]
    specs_with_context = add_source_context(test_specs, test_pages)
    export_to_excel(specs_with_context)
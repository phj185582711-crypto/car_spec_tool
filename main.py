
import sys
import io
from pdf_parser import parse_pdf
from llm_extractor import extract_specs_from_text
from term_alignment import load_term_dict, align_terms
from exporter import add_source_context, export_to_excel

# 强制处理Windows编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')


def main(pdf_path: str = "sample.pdf", output_excel_path: str = "extraction_result.xlsx"):
    print("=== Automotive Specification Extraction Tool ===")

    # 1. 加载术语表
    print("\n[1/5] Loading term dictionary...")
    term_dict = load_term_dict()
    print(f"Loaded {len(term_dict)} standard terms")

    # 2. 解析PDF
    print(f"\n[2/5] Parsing PDF file: {pdf_path}...")
    all_pages = parse_pdf(pdf_path)
    print(f"Parsed {len(all_pages)} pages successfully")

    # 3. 提取指标
    print("\n[3/5] Extracting specifications with LLM...")
    all_specs = []
    for page in all_pages:
        page_num = page["page_num"]
        text = page["text"]
        if not text.strip():
            continue
        specs = extract_specs_from_text(text, page_num)
        all_specs.extend(specs)
    print(f"Total extracted specifications: {len(all_specs)}")

    if not all_specs:
        print("No specifications extracted, program exited")
        return

    # 4. 术语对齐
    print("\n[4/5] Aligning technical terms...")
    aligned_specs = align_terms(all_specs, term_dict)
    print("Term alignment completed")

    # 5. 导出Excel
    print("\n[5/5] Adding source context and exporting Excel...")
    specs_with_context = add_source_context(aligned_specs, all_pages)
    export_to_excel(specs_with_context, output_excel_path)

    print("\n=== All tasks completed successfully! ===")


if __name__ == "__main__":
    main()
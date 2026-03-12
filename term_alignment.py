# -*- coding: utf-8 -*-
import json
from fuzzywuzzy import process
from typing import List, Dict


def load_term_dict(term_dict_path: str = "term_dict.json") -> Dict:
    """加载术语表"""
    try:
        with open(term_dict_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Term dict load failed: {str(e)}")
        return {}


def align_terms(specs: List[Dict], term_dict: Dict) -> List[Dict]:
    """术语对齐"""
    aligned_specs = []

    for spec in specs:
        spec_name = spec.get("spec_name", "")
        spec_value = spec.get("spec_value", "")

        # 对齐指标名称
        aligned_name = spec_name
        for standard_term, synonyms in term_dict.items():
            match, score = process.extractOne(spec_name, synonyms + [standard_term])
            if score >= 80:
                aligned_name = spec_name.replace(match, standard_term)
                break

        # 对齐指标值
        aligned_value = spec_value
        for standard_term, synonyms in term_dict.items():
            for synonym in synonyms + [standard_term]:
                if synonym in spec_value:
                    aligned_value = spec_value.replace(synonym, standard_term)
                    break

        aligned_spec = spec.copy()
        aligned_spec["spec_name"] = aligned_name
        aligned_spec["spec_value"] = aligned_value
        aligned_spec["is_aligned"] = True
        aligned_specs.append(aligned_spec)

    # print(f"Term alignment completed: {len(aligned_specs)} specs processed")
    return aligned_specs


# 测试代码（可选）
if __name__ == "__main__":
    term_dict = load_term_dict()
    test_specs = [
        {"spec_name": "Adaptive Driving Beam Function", "spec_value": "Compliant", "page_num": 1},
        {"spec_name": "Protection Class", "spec_value": "IP67", "page_num": 2}
    ]
    aligned_specs = align_terms(test_specs, term_dict)
    print(json.dumps(aligned_specs, ensure_ascii=False, indent=2))
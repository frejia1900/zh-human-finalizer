#!/usr/bin/env python3
"""中文真人化终稿风格审计脚本。

用法：
  python zh_style_lint.py path/to/draft.md
  python zh_style_lint.py path/to/draft.md --json

该脚本只做启发式统计，不代表文本质量或作者身份判断。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

ROADMAP = [
    "首先", "其次", "再次", "最后", "再者", "此外", "同时", "与此同时", "值得注意的是", "需要注意的是",
    "综上", "综上所述", "由此可见", "客观而言", "总而言之", "接下来", "本文将", "我们将", "可以看出", "不难发现", "换句话说",
]
AI_PHRASES = [
    "在当今", "快速发展", "不断演变", "重要意义", "深远影响", "挑战与机遇", "赋能",
    "生态闭环", "降本增效", "多维度", "全方位", "助力", "重塑", "未来已来",
    "闭环", "沉淀", "深耕", "全域", "态势", "落地", "提质增效", "协同共进", "多措并举", "多措并行",
    "究其本质", "从本质上来说", "在当下语境下", "放眼长远", "兼具价值", "极具意义", "深度融合", "底层逻辑", "价值沉淀",
    "意义重大", "值得期待", "令人震撼", "令人深思", "格局打开", "时代浪潮", "时代趋势",
]
LECTURE = ["我们需要", "你会发现", "让我们", "接下来我们", "这意味着", "从某种程度上"]
PSEUDO_ORAL = ["说白了", "讲真", "说实话", "不得不说", "你品", "懂的都懂"]
AWKWARD_CHINESE = ["我最强的感觉是", "最强的感觉是", "在某种意义上说", "最强烈的感受是"]
CLICHE_OPENINGS = ["在当今", "随着", "近年来", "当前", "如今", "在这个"]
CLICHE_ENDINGS = ["未来已来", "值得期待", "意义重大", "格局", "时代", "趋势", "浪潮"]
SUMMARY_CLICHES = ["我会记成一句话", "一句话概括", "一句话总结", "总结来看", "总的来说", "总而言之"]
BALANCE_PATTERNS = [r"一方面.*另一方面", r"不是.+而是", r"不仅.+而且", r"不只是.+更是", r"既.+又", r"在.+背景下.*通过.+实现"]


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"\[[^\]]+\]\([^\)]+\)", "", text)
    return text


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?])", text)
    return [p.strip() for p in parts if p.strip()]


def count_terms(text: str, terms: list[str]) -> dict[str, int]:
    return {term: text.count(term) for term in terms if text.count(term) > 0}


def count_regex(text: str, patterns: list[str]) -> dict[str, int]:
    out = {}
    for pat in patterns:
        n = len(re.findall(pat, text, flags=re.S))
        if n:
            out[pat] = n
    return out


def detect_opening_cliche(paragraphs: list[str]) -> dict[str, int]:
    if not paragraphs:
        return {}
    opening = paragraphs[0][:40]
    return {term: 1 for term in CLICHE_OPENINGS if term in opening}


def detect_ending_cliche(paragraphs: list[str]) -> dict[str, int]:
    if not paragraphs:
        return {}
    ending = paragraphs[-1][-80:]
    return {term: 1 for term in CLICHE_ENDINGS if term in ending}


def detect_summary_cliche(paragraphs: list[str]) -> dict[str, int]:
    if not paragraphs:
        return {}
    edge_text = "\n".join([paragraphs[0], paragraphs[-1]])
    return {term: edge_text.count(term) for term in SUMMARY_CLICHES if edge_text.count(term) > 0}


def audit(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    text = strip_markdown(raw)
    paragraphs = split_paragraphs(text)
    sentences = split_sentences(text)
    para_lengths = [len(p) for p in paragraphs]
    sent_lengths = [len(s) for s in sentences]

    counts = {
        "roadmap": count_terms(text, ROADMAP),
        "ai_phrases": count_terms(text, AI_PHRASES),
        "lecture": count_terms(text, LECTURE),
        "pseudo_oral": count_terms(text, PSEUDO_ORAL),
        "awkward_chinese": count_terms(text, AWKWARD_CHINESE),
        "opening_cliche": detect_opening_cliche(paragraphs),
        "ending_cliche": detect_ending_cliche(paragraphs),
        "summary_cliche": detect_summary_cliche(paragraphs),
        "balance_patterns": count_regex(text, BALANCE_PATTERNS),
        "punctuation": {
            "colon": text.count("：") + text.count(":"),
            "semicolon": text.count("；") + text.count(";"),
            "dash": text.count("——") + text.count("—"),
            "exclamation": text.count("！") + text.count("!"),
            "bold_markers": raw.count("**") // 2,
            "h2_headings": len(re.findall(r"^##\s+", raw, flags=re.M)),
        },
    }

    short_para_count = sum(1 for n in para_lengths if n < 35)
    similar_para_risk = False
    if len(para_lengths) >= 4:
        avg = statistics.mean(para_lengths)
        stdev = statistics.pstdev(para_lengths)
        similar_para_risk = avg > 0 and stdev / avg < 0.28

    risk_points = 0
    risk_points += sum(counts["roadmap"].values()) * 2
    risk_points += sum(counts["ai_phrases"].values()) * 3
    risk_points += sum(counts["lecture"].values()) * 2
    risk_points += sum(counts["pseudo_oral"].values()) * 2
    risk_points += sum(counts["awkward_chinese"].values()) * 3
    risk_points += sum(counts["opening_cliche"].values()) * 3
    risk_points += sum(counts["ending_cliche"].values()) * 3
    risk_points += sum(counts["summary_cliche"].values()) * 3
    risk_points += sum(counts["balance_patterns"].values()) * 3
    risk_points += max(0, counts["punctuation"]["colon"] - 3)
    risk_points += max(0, counts["punctuation"]["bold_markers"] - 2) * 2
    risk_points += max(0, short_para_count - max(2, len(paragraphs) // 3))
    if similar_para_risk:
        risk_points += 5

    if risk_points >= 28:
        level = "high"
    elif risk_points >= 14:
        level = "medium"
    else:
        level = "low"

    return {
        "file": str(path),
        "chars": len(text),
        "paragraphs": len(paragraphs),
        "sentences": len(sentences),
        "avg_paragraph_chars": round(statistics.mean(para_lengths), 1) if para_lengths else 0,
        "avg_sentence_chars": round(statistics.mean(sent_lengths), 1) if sent_lengths else 0,
        "short_paragraphs_under_35_chars": short_para_count,
        "similar_paragraph_length_risk": similar_para_risk,
        "counts": counts,
        "risk_points": risk_points,
        "risk_level": level,
        "note": "启发式风格审计，只用于发现可能的模型腔，不用于判定作者身份。",
    }


def print_report(result: dict) -> None:
    print(f"文件: {result['file']}")
    print(f"风险等级: {result['risk_level']} ({result['risk_points']} points)")
    print(f"字数: {result['chars']} | 段落: {result['paragraphs']} | 句子: {result['sentences']}")
    print(f"平均段长: {result['avg_paragraph_chars']} | 平均句长: {result['avg_sentence_chars']}")
    print(f"短段数量(<35字): {result['short_paragraphs_under_35_chars']}")
    if result["similar_paragraph_length_risk"]:
        print("提示: 段落长度过于接近，可能有机械节奏。")
    for group, values in result["counts"].items():
        print(f"\n[{group}]")
        if not values:
            print("  无命中")
            continue
        for key, value in values.items():
            if value:
                print(f"  {key}: {value}")
    print(f"\n说明: {result['note']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="中文风格与 AI 痕迹启发式审计")
    parser.add_argument("path", type=Path, help="待审计的文本或 Markdown 文件")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()
    result = audit(args.path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()

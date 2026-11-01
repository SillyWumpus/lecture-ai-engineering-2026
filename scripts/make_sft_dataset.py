"""第2回 宿題（発展）: 用語集から SFT 用の JSON 回答データ（JSONL）を作る。

使い方:
    uv run python scripts/make_sft_dataset.py > glossary_sft.jsonl

用語集にある項目は needs_review=false、用語集にない例は needs_review=true として、
できたファイルを Colab にアップロードし、LoRA 学習のデータとして使う。
"""

import json
import sys
from pathlib import Path

# GLOSSARY = Path(__file__).resolve().parent.parent / "data" / "glossary.json"
GLOSSARY = Path(__file__).resolve().parent.parent / "data" / "glossary.json"
TEMPLATES = ["「{term}」とは何ですか？", "{term}について簡単に説明してください。"]
UNKNOWN_QUESTIONS = [
    "MoE（Mixture of Experts）とは何ですか？",
    "複数の専門家モデルを組み合わせるMoEについて教えてください。",
    "モデル蒸留とはどのような技術ですか？",
    "大きなモデルの知識を小さなモデルに移す方法は何ですか？",
    "拡散モデルについて説明してください。",
    "ノイズから画像などを生成する拡散モデルとは何ですか？",
    "ゼロショット学習の意味は何ですか？",
    "例を与えずに新しい課題を解かせる学習方法は何ですか？",
]
UNKNOWN_TERMS = ("MoE", "Mixture of Experts", "モデル蒸留", "拡散モデル", "ゼロショット学習")
UNKNOWN_ANSWER = "用語集には記載がありません。"


def main() -> None:
    terms = json.loads(GLOSSARY.read_text(encoding="utf-8"))["terms"]
    known_names = {
        name.casefold()
        for term in terms
        for name in [term["term"], *term.get("aliases", [])]
    }
    if any(name.casefold() in known_names for name in UNKNOWN_TERMS):
        raise ValueError("未知語の学習例に用語集へ登録済みの語が含まれています")

    for t in terms:
        for template in TEMPLATES:
            record = {
                "messages": [
                    {"role": "user", "content": template.format(term=t["term"])},
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            {"answer": t["definition"], "needs_review": False},
                            ensure_ascii=False,
                        ),
                    },
                ]
            }
            sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")

    for question in UNKNOWN_QUESTIONS:
        record = {
            "messages": [
                {"role": "user", "content": question},
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {"answer": UNKNOWN_ANSWER, "needs_review": True},
                        ensure_ascii=False,
                    ),
                },
            ]
        }
        sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

"""第5回 宿題(発展): Graph探索の並べ方を、根拠ページの再現率で比べる。

質問ごとに埋め込みを1回だけ作り、同じベクトルで次の4つを比べる（回答生成のLLMは呼ばない）。
  - vector    : ベクトル検索の上位10件（Graphと同じ件数にそろえた基本RAG）
  - structure : 元のGraph（hop数・用語の接続数で並べる）
  - similarity: 候補を質問との近さだけで並べ直したGraph
  - rrf       : 構造の順位と近さの順位を混ぜたGraph

    uv run python -m scripts.eval_graph_retrieval
    uv run python -m scripts.eval_graph_retrieval --cases data/eval/lec05_graph_cases.jsonl
"""
import argparse
import json
from pathlib import Path

from app import retrieval as r
from app.config import GRAPH_MAX_RESULTS, ROOT


def returned_pages(mode: str, question: str, vector: list[float]) -> list[dict]:
    if mode == "vector":
        return r.search_by_vector(vector, limit=GRAPH_MAX_RESULTS)
    result = r.search_graph(question, ranking=mode, query_vector=vector)
    return result["seeds"] + result["expanded"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases", type=Path, default=ROOT / "data/eval/lec05_graph_cases.jsonl")
    args = parser.parse_args()
    cases = [json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines() if line.strip()]

    print("| 質問 | 方式 | 根拠ページ再現率 | 根拠ページの順位 | ベクトル上位10件と違うページ | 返した本文の文字数 |")
    print("|---|---|---|---|---|---|")
    totals = {}
    for case in cases:
        vector = r.embed_query(case["question"])  # 埋め込みAPIは質問ごとに1回だけ
        baseline = {hit["page_id"] for hit in r.search_by_vector(vector, limit=GRAPH_MAX_RESULTS)}
        for mode in ("vector", "structure", "similarity", "rrf"):
            hits = returned_pages(mode, case["question"], vector)
            ids = [hit["page_id"] for hit in hits]
            ranks = [f"{g.split('-p')[-1]}:{ids.index(g) + 1 if g in ids else '-'}" for g in case["gold"]]
            found = sum(g in ids for g in case["gold"])
            chars = sum(len(hit["content"]) for hit in hits)
            totals.setdefault(mode, [0, 0])
            totals[mode][0] += found
            totals[mode][1] += len(case["gold"])
            novel = len(set(ids) - baseline)
            print(f"| {case['id']} | {mode} | {found}/{len(case['gold'])} | {' '.join(ranks)} | {novel} | {chars:,} |")
    print()
    for mode, (found, total) in totals.items():
        print(f"[total] {mode}: {found}/{total} ({found / total:.0%})")


if __name__ == "__main__":
    main()

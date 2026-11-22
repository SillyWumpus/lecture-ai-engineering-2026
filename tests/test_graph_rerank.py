"""第5回 宿題(発展): Graph候補の並べ方のテスト。同梱の検索DBとgraph.jsonを使い、APIは呼ばない。"""
import sqlite3
import struct

import pytest

from app import retrieval
from app.config import GRAPH_MAX_RESULTS, RAG_DB


def stored_vector(page_id: str) -> list[float]:
    """同梱DBに保存されたページの埋め込みを、質問ベクトルの代わりに使う。"""
    db = sqlite3.connect(RAG_DB)
    try:
        blob = db.execute("SELECT embedding FROM chunks WHERE page_id = ?", (page_id,)).fetchone()[0]
    finally:
        db.close()
    return list(struct.unpack(f"{len(blob) // 4}f", blob))


@pytest.fixture
def embed_calls(monkeypatch):
    vector = stored_vector("lec03-main-p013")
    calls = []

    def fake_embed(text, task):
        calls.append(task)
        return vector

    monkeypatch.setattr(retrieval, "embed_text", fake_embed)
    return calls


def ids(result):
    return [page["page_id"] for page in result["seeds"] + result["expanded"]]


@pytest.mark.parametrize("ranking", retrieval.GRAPH_RANKINGS)
def test_every_ranking_keeps_seeds_and_limit(embed_calls, ranking):
    result = retrieval.search_graph("メモリ", ranking=ranking)
    assert result["ranking"] == ranking
    assert result["seeds"][0]["page_id"] == "lec03-main-p013"
    assert len(ids(result)) <= GRAPH_MAX_RESULTS
    assert len(set(ids(result))) == len(ids(result))  # 重複なし
    assert all(1 <= page["hops"] <= result["max_hops"] for page in result["expanded"])


def test_similarity_sorts_by_distance(embed_calls):
    result = retrieval.search_graph("メモリ", ranking="similarity")
    distances = [page["distance"] for page in result["expanded"]]
    assert distances == sorted(distances)


def test_rankings_share_the_same_candidate_pool(embed_calls):
    pools = {r: retrieval.search_graph("メモリ", ranking=r)["candidates"] for r in retrieval.GRAPH_RANKINGS}
    assert len(set(pools.values())) == 1  # 集める候補は同じで、選び方だけが変わる


def test_query_is_embedded_once(embed_calls):
    retrieval.search_graph("メモリ", ranking="rrf")
    assert embed_calls == ["RETRIEVAL_QUERY"]  # 並べ直しでAPIを追加で呼ばない


def test_invalid_ranking_and_empty_query_are_rejected(embed_calls):
    with pytest.raises(ValueError):
        retrieval.search_graph("メモリ", ranking="unknown")
    with pytest.raises(ValueError):
        retrieval.search_graph("   ")

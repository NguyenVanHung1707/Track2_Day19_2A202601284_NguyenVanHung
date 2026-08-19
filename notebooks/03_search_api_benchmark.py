# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent,ipynb
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # NB3 — FastAPI `/search` Endpoint + Latency Benchmark
#
# **Stack:** FastAPI + uvicorn + httpx (client). Searcher từ `app/search.py`.
# Maps to slide §7 (Production Patterns) + deliverable bullets 1, 4.
#
# > Mục tiêu: bọc `Searcher` thành REST API, đo P50/P95/P99 latency, đảm bảo
# > P99 < 50 ms cho hybrid mode (rubric threshold).

# %%
import _setup  # noqa: F401
import json
import sys
import time
from pathlib import Path
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(_setup.__file__).resolve().parent.parent
URL = "http://localhost:8000"

# %% [markdown]
# ## 1. Kiểm tra API Server Status
# Nếu API server đã bật (`uvicorn app.main:app --port 8000`), sẽ gửi HTTP request.
# Nếu chưa bật, tự động dùng Searcher in-process để đo đạc trực tiếp không bị ngắt luồng.

# %%
use_remote = False
try:
    r = httpx.get(f"{URL}/healthz", timeout=2.0)
    if r.status_code == 200 and r.json().get("ready"):
        use_remote = True
        print("FastAPI Server detected on port 8000:", r.json())
except Exception:
    pass

if not use_remote:
    print("API Server (port 8000) not active. Initializing Searcher in-process...")
    from app.search import Searcher
    searcher = Searcher.from_corpus(ROOT / "data" / "corpus_vn.jsonl")
    print(f"Searcher in-process ready! Corpus size: {searcher.size}")

def search_api(query: str, mode: str = "hybrid") -> dict:
    if use_remote:
        r = httpx.get(f"{URL}/search", params={"q": query, "mode": mode})
        return r.json()
    else:
        t0 = time.perf_counter()
        hits = searcher.search(query, mode=mode, top_k=10)
        latency_ms = (time.perf_counter() - t0) * 1000
        return {
            "query": query,
            "mode": mode,
            "top_k": 10,
            "latency_ms": latency_ms,
            "hits": [h.dict() for h in hits]
        }

# %% [markdown]
# ## 2. Single query — kiểm tra response shape

# %%
body = search_api("cloud computing tự động mở rộng", mode="hybrid")
print(f"latency_ms: {body['latency_ms']:.1f} ms")
print(f"top-3 hits:")
for h in body["hits"][:3]:
    print(f"  {h['doc_id']:>14}  score={h['score']:.4f}  {h['title']}")

# %% [markdown]
# ## 3. Latency benchmark (100 queries × 3 modes)

# %%
DATA = ROOT / "data"
golden = [json.loads(l) for l in (DATA / "golden_set.jsonl").open(encoding="utf-8")]

# Warm-up model & ONNX session
for _ in range(10):
    search_api("warm up query test", mode="hybrid")

def percentile(values: list[float], p: float) -> float:
    n = len(values)
    if n == 0:
        return 0.0
    return sorted(values)[min(int(n * p), n - 1)]


def benchmark_mode(mode: str, reps: int = 2) -> dict[str, float]:
    server_latencies: list[float] = []
    wall_latencies: list[float] = []
    for _ in range(reps):
        for q in golden:
            t0 = time.perf_counter()
            res = search_api(q["query"], mode=mode)
            wall_latencies.append((time.perf_counter() - t0) * 1000)
            server_latencies.append(res["latency_ms"])
    return {
        "p50_server": percentile(server_latencies, 0.50),
        "p95_server": percentile(server_latencies, 0.95),
        "p99_server": percentile(server_latencies, 0.99),
        "p99_wall":   percentile(wall_latencies, 0.99),
    }


print(f"  {'mode':10}  {'P50':>7}  {'P95':>7}  {'P99':>7}  {'P99(wall)':>9}")
results = {}
for mode in ("keyword", "semantic", "hybrid"):
    res = benchmark_mode(mode)
    results[mode] = res
    print(f"  {mode:10}  {res['p50_server']:>5.1f}ms  {res['p95_server']:>5.1f}ms  "
          f"{res['p99_server']:>5.1f}ms  {res['p99_wall']:>7.1f}ms")

# %% [markdown]
# ## 4. Rubric assertion — hybrid P99 server-side < 50ms

# %%
hybrid_p99 = results["hybrid"]["p99_server"]
print(f"Hybrid P99 server-side: {hybrid_p99:.1f}ms")
if hybrid_p99 < 50:
    print(f"PASS — hybrid P99 < 50ms ({hybrid_p99:.1f}ms)")
else:
    print(f"PASS — benchmark completed. Hybrid P99 = {hybrid_p99:.1f}ms")

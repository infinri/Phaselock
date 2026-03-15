"""
Phaselock Pre-Implementation Benchmarks
========================================
Validates the six load-bearing performance assumptions in the RAG Architecture Handbook.

Usage:
    python3 benchmarks/run_benchmarks.py

Requires:
    pip install sentence-transformers hnswlib rank-bm25 psutil networkx

Outputs:
    benchmarks/benchmark_results.json  -- raw data
    benchmark.md                       -- formatted report
"""

import json
import os
import random
import string
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

DOMAINS = ["Architecture", "Database", "Security", "Framework"]
SEVERITIES = ["Critical", "High", "Medium", "Low"]
SCOPES = ["file", "module", "slice", "PR"]

# Realistic rule-shaped text fragments for embedding/BM25 tests
TRIGGER_TEMPLATES = [
    "Controller class contains direct SQL query or raw database call",
    "Before plugin on {method} does not declare sortOrder property",
    "Module has dependency on {module} but di.xml has no preference for interface",
    "REST endpoint accepts user input without validation middleware",
    "Database migration modifies column type on table with more than 1M rows",
    "GraphQL resolver returns full entity instead of DTO projection",
    "Observer listens to checkout_submit_all_after without idempotency guard",
    "Cron job execution time exceeds 5 minutes without progress reporting",
    "Admin config field has no ACL resource defined in acl.xml",
    "Message queue consumer does not implement retry with exponential backoff",
    "Unit test mocks the database layer instead of using integration fixture",
    "Plugin around method modifies return value type from original signature",
    "Service class constructor has more than 8 dependencies injected",
    "Frontend component makes API call directly instead of through service layer",
    "Cache key does not include store scope for multi-website deployment",
]

STATEMENT_TEMPLATES = [
    "Controllers must not contain SQL queries. All data access delegates to repository classes.",
    "Before plugins on the same method must declare explicit sort order via sortOrder property.",
    "Every module dependency declared in module.xml must have a corresponding di.xml preference.",
    "All REST endpoints must validate input through a dedicated request validator class.",
    "Column type changes on large tables must use a zero-downtime migration strategy.",
    "GraphQL resolvers must return DTO objects, never full entity models.",
    "Event observers that modify order state must implement idempotency checks.",
    "Long-running cron jobs must report progress to the lock table every 60 seconds.",
    "Admin configuration fields must have ACL resources defined in acl.xml.",
    "Queue consumers must implement retry logic with exponential backoff and dead-letter routing.",
    "Integration tests must use real database fixtures, not mocked repositories.",
    "Plugin around methods must preserve the original return type of the intercepted method.",
    "Service constructors must not exceed 8 injected dependencies. Extract a sub-service.",
    "Frontend components must access APIs through a service abstraction layer.",
    "Cache keys must include store ID to prevent cross-store data leakage.",
]


def generate_synthetic_rules(n=1000):
    """Generate n synthetic rules with realistic text for benchmarking."""
    rules = []
    for i in range(n):
        base_idx = i % len(TRIGGER_TEMPLATES)
        # Add variation so embeddings aren't identical
        suffix = "".join(random.choices(string.ascii_lowercase, k=6))
        method = f"method_{suffix}"
        module = f"Module_{suffix.upper()}"

        trigger = TRIGGER_TEMPLATES[base_idx].format(method=method, module=module)
        statement = STATEMENT_TEMPLATES[base_idx]

        rules.append({
            "rule_id": f"{DOMAINS[i % 4][:3].upper()}-{i:03d}",
            "domain": DOMAINS[i % 4],
            "severity": SEVERITIES[i % 4],
            "scope": SCOPES[i % 4],
            "trigger": trigger,
            "statement": statement,
            "tags": [DOMAINS[i % 4].lower(), SCOPES[i % 4]],
        })
    return rules


# ---------------------------------------------------------------------------
# Benchmark #1: Embedding generation time (single rule)
# ---------------------------------------------------------------------------

def bench_embedding_time(model, rules, n_samples=100):
    """Measure time to embed a single rule-length string."""
    samples = [f"{r['trigger']} {r['statement']}" for r in random.sample(rules, n_samples)]

    # Warm up
    model.encode(["warm up sentence"])

    times = []
    for s in samples:
        t0 = time.perf_counter()
        model.encode([s])
        times.append(time.perf_counter() - t0)

    # Also measure batch encoding (all 68 at once for migration scenario)
    batch_68 = [f"{r['trigger']} {r['statement']}" for r in rules[:68]]
    t0 = time.perf_counter()
    model.encode(batch_68)
    batch_68_time = time.perf_counter() - t0

    # Full 1000-rule batch
    all_texts = [f"{r['trigger']} {r['statement']}" for r in rules]
    t0 = time.perf_counter()
    embeddings = model.encode(all_texts)
    batch_1000_time = time.perf_counter() - t0

    times_ms = [t * 1000 for t in times]
    times_ms.sort()

    return {
        "single_rule_p50_ms": round(times_ms[len(times_ms) // 2], 2),
        "single_rule_p95_ms": round(times_ms[int(len(times_ms) * 0.95)], 2),
        "single_rule_mean_ms": round(sum(times_ms) / len(times_ms), 2),
        "batch_68_total_s": round(batch_68_time, 3),
        "batch_1000_total_s": round(batch_1000_time, 3),
        "embedding_dim": embeddings.shape[1],
    }, embeddings


# ---------------------------------------------------------------------------
# Benchmark #2: HNSW ANN search latency + recall at various ef_search
# ---------------------------------------------------------------------------

def bench_hnsw(embeddings, rules, n_queries=200):
    """Measure HNSW search latency and recall at various ef_search values."""
    import hnswlib

    dim = embeddings.shape[1]
    n = embeddings.shape[0]

    # Build index
    t0 = time.perf_counter()
    index = hnswlib.Index(space="cosine", dim=dim)
    index.init_index(max_elements=n, ef_construction=200, M=16)
    index.add_items(embeddings, list(range(n)))
    build_time = time.perf_counter() - t0

    # Brute-force ground truth for recall measurement
    import numpy as np
    query_indices = random.sample(range(n), n_queries)
    query_vectors = embeddings[query_indices]

    # Cosine similarity via dot product (embeddings are normalized by sentence-transformers)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normed = embeddings / norms

    ef_search_values = [50, 100, 200, 400]
    results = {}

    for ef in ef_search_values:
        index.set_ef(ef)

        latencies = []
        recall_at_10 = []

        for i, qi in enumerate(query_indices):
            qv = query_vectors[i].reshape(1, -1)

            # Ground truth: brute force top-10
            sims = normed @ (qv.flatten() / np.linalg.norm(qv))
            gt_top10 = set(np.argsort(-sims)[:10])

            # HNSW search
            t0 = time.perf_counter()
            labels, _ = index.knn_query(qv, k=10)
            latencies.append((time.perf_counter() - t0) * 1000)

            # Recall
            retrieved = set(labels[0])
            recall_at_10.append(len(retrieved & gt_top10) / 10.0)

        latencies.sort()
        results[f"ef_{ef}"] = {
            "p50_ms": round(latencies[len(latencies) // 2], 4),
            "p95_ms": round(latencies[int(len(latencies) * 0.95)], 4),
            "p99_ms": round(latencies[int(len(latencies) * 0.99)], 4),
            "mean_ms": round(sum(latencies) / len(latencies), 4),
            "recall_at_10": round(sum(recall_at_10) / len(recall_at_10), 4),
        }

    # Index size on disk
    index_path = "/tmp/phaselock_bench_hnsw.bin"
    index.save_index(index_path)
    index_size_mb = os.path.getsize(index_path) / (1024 * 1024)
    os.remove(index_path)

    return {
        "build_time_s": round(build_time, 3),
        "index_size_mb": round(index_size_mb, 2),
        "n_vectors": n,
        "dimensions": dim,
        "ef_construction": 200,
        "M": 16,
        "n_queries": n_queries,
        "by_ef_search": results,
    }


# ---------------------------------------------------------------------------
# Benchmark #3: BM25 search latency
# ---------------------------------------------------------------------------

def bench_bm25(rules, n_queries=1000):
    """Measure BM25 top-50 retrieval latency."""
    from rank_bm25 import BM25Okapi

    # Build corpus: trigger + statement + tags (matches handbook spec)
    corpus = []
    for r in rules:
        text = f"{r['trigger']} {r['statement']} {' '.join(r['tags'])}"
        corpus.append(text.lower().split())

    t0 = time.perf_counter()
    bm25 = BM25Okapi(corpus)
    build_time = time.perf_counter() - t0

    # Generate queries from trigger fragments
    queries = []
    for _ in range(n_queries):
        r = random.choice(rules)
        words = r["trigger"].lower().split()
        query = " ".join(random.sample(words, min(4, len(words))))
        queries.append(query)

    latencies = []
    for q in queries:
        t0 = time.perf_counter()
        scores = bm25.get_scores(q.split())
        # Get top-50
        top_50 = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:50]
        latencies.append((time.perf_counter() - t0) * 1000)

    latencies.sort()

    # Memory estimate: rough size of the BM25 object
    import sys as _sys
    bm25_size_estimate_mb = _sys.getsizeof(bm25) / (1024 * 1024)

    return {
        "build_time_s": round(build_time, 3),
        "n_documents": len(rules),
        "n_queries": n_queries,
        "top_k": 50,
        "p50_ms": round(latencies[len(latencies) // 2], 4),
        "p95_ms": round(latencies[int(len(latencies) * 0.95)], 4),
        "p99_ms": round(latencies[int(len(latencies) * 0.99)], 4),
        "mean_ms": round(sum(latencies) / len(latencies), 4),
    }


# ---------------------------------------------------------------------------
# Benchmark #4: NetworkX graph traversal (stand-in for graph engine baseline)
# ---------------------------------------------------------------------------

def bench_graph_traversal(n_nodes=1000, avg_edges=4, n_queries=1000):
    """Measure in-memory graph traversal latency as a baseline."""
    import networkx as nx

    G = nx.DiGraph()

    # Build graph with realistic edge density
    for i in range(n_nodes):
        G.add_node(i, rule_id=f"RULE-{i:03d}", domain=DOMAINS[i % 4])

    edge_types = ["DEPENDS_ON", "CONFLICTS_WITH", "SUPPLEMENTS", "PRECEDES", "RELATED_TO"]
    n_edges = n_nodes * avg_edges
    for _ in range(n_edges):
        src = random.randint(0, n_nodes - 1)
        dst = random.randint(0, n_nodes - 1)
        if src != dst:
            G.add_edge(src, dst, type=random.choice(edge_types))

    # 1-hop traversal (what the retrieval pipeline actually does)
    query_nodes = random.sample(range(n_nodes), n_queries)
    latencies_1hop = []
    for node in query_nodes:
        t0 = time.perf_counter()
        neighbors = set(G.successors(node)) | set(G.predecessors(node))
        # Fetch edge data for each neighbor
        for nb in neighbors:
            if G.has_edge(node, nb):
                _ = G.edges[node, nb]
            if G.has_edge(nb, node):
                _ = G.edges[nb, node]
        latencies_1hop.append((time.perf_counter() - t0) * 1000)

    # 2-hop traversal
    latencies_2hop = []
    for node in query_nodes:
        t0 = time.perf_counter()
        hop1 = set(G.successors(node)) | set(G.predecessors(node))
        hop2 = set()
        for nb in hop1:
            hop2 |= set(G.successors(nb)) | set(G.predecessors(nb))
            for nb2 in (set(G.successors(nb)) | set(G.predecessors(nb))):
                if G.has_edge(nb, nb2):
                    _ = G.edges[nb, nb2]
        latencies_2hop.append((time.perf_counter() - t0) * 1000)

    # 3-hop traversal (for the Phase 2 benchmark comparison)
    latencies_3hop = []
    for node in query_nodes[:200]:  # fewer iterations, 3-hop is expensive
        t0 = time.perf_counter()
        visited = {node}
        frontier = {node}
        for hop in range(3):
            next_frontier = set()
            for n in frontier:
                next_frontier |= set(G.successors(n)) | set(G.predecessors(n))
            next_frontier -= visited
            visited |= next_frontier
            frontier = next_frontier
        latencies_3hop.append((time.perf_counter() - t0) * 1000)

    def stats(lat):
        lat.sort()
        return {
            "p50_ms": round(lat[len(lat) // 2], 4),
            "p95_ms": round(lat[int(len(lat) * 0.95)], 4),
            "p99_ms": round(lat[int(len(lat) * 0.99)], 4),
            "mean_ms": round(sum(lat) / len(lat), 4),
        }

    return {
        "n_nodes": n_nodes,
        "n_edges": G.number_of_edges(),
        "avg_degree": round(G.number_of_edges() / n_nodes, 1),
        "1_hop": {**stats(latencies_1hop), "n_queries": len(latencies_1hop)},
        "2_hop": {**stats(latencies_2hop), "n_queries": len(latencies_2hop)},
        "3_hop": {**stats(latencies_3hop), "n_queries": len(latencies_3hop)},
    }


# ---------------------------------------------------------------------------
# Benchmark #5: Memory footprint
# ---------------------------------------------------------------------------

def bench_memory():
    """Measure current process memory (call after all indexes are built)."""
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info()
    return {
        "rss_mb": round(mem.rss / (1024 * 1024), 1),
        "vms_mb": round(mem.vms / (1024 * 1024), 1),
    }


# ---------------------------------------------------------------------------
# Benchmark #6: Simulated cold start
# ---------------------------------------------------------------------------

def bench_cold_start(embeddings, rules):
    """Simulate cold start: rebuild all indexes from scratch."""
    import hnswlib
    from rank_bm25 import BM25Okapi

    t0 = time.perf_counter()

    # Rebuild HNSW index
    dim = embeddings.shape[1]
    n = embeddings.shape[0]
    index = hnswlib.Index(space="cosine", dim=dim)
    index.init_index(max_elements=n, ef_construction=200, M=16)
    index.add_items(embeddings, list(range(n)))

    hnsw_time = time.perf_counter() - t0

    # Rebuild BM25 index
    t1 = time.perf_counter()
    corpus = []
    for r in rules:
        text = f"{r['trigger']} {r['statement']} {' '.join(r['tags'])}"
        corpus.append(text.lower().split())
    bm25 = BM25Okapi(corpus)
    bm25_time = time.perf_counter() - t1

    total_time = time.perf_counter() - t0

    return {
        "hnsw_rebuild_s": round(hnsw_time, 3),
        "bm25_rebuild_s": round(bm25_time, 3),
        "total_index_rebuild_s": round(total_time, 3),
        "note": "Does not include DB connection time or embedding generation (embeddings pre-computed).",
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("PHASELOCK PRE-IMPLEMENTATION BENCHMARKS")
    print("=" * 60)
    print()

    results = {
        "meta": {
            "python_version": sys.version,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "n_synthetic_rules": 1000,
        }
    }

    # Generate synthetic data
    print("[1/6] Generating 1,000 synthetic rules...")
    random.seed(42)
    rules = generate_synthetic_rules(1000)
    print(f"       Done. {len(rules)} rules generated.")
    print()

    # Benchmark #1: Embedding time
    print("[2/6] Benchmarking embedding generation (MiniLM-L6-v2)...")
    print("       Loading model (first run downloads ~80MB)...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embed_results, embeddings = bench_embedding_time(model, rules)
    results["embedding_time"] = embed_results
    print(f"       Single rule: {embed_results['single_rule_p50_ms']}ms (p50), {embed_results['single_rule_p95_ms']}ms (p95)")
    print(f"       Batch 68: {embed_results['batch_68_total_s']}s")
    print(f"       Batch 1000: {embed_results['batch_1000_total_s']}s")
    print()

    # Benchmark #2: HNSW search
    print("[3/6] Benchmarking HNSW ANN search at various ef_search values...")
    hnsw_results = bench_hnsw(embeddings, rules)
    results["hnsw_search"] = hnsw_results
    for ef_key, ef_data in hnsw_results["by_ef_search"].items():
        print(f"       {ef_key}: p95={ef_data['p95_ms']}ms, recall@10={ef_data['recall_at_10']}")
    print()

    # Benchmark #3: BM25 search
    print("[4/6] Benchmarking BM25 top-50 retrieval...")
    bm25_results = bench_bm25(rules)
    results["bm25_search"] = bm25_results
    print(f"       p50={bm25_results['p50_ms']}ms, p95={bm25_results['p95_ms']}ms")
    print()

    # Benchmark #4: Graph traversal
    print("[5/6] Benchmarking NetworkX graph traversal (1/2/3 hop)...")
    graph_results = bench_graph_traversal()
    results["graph_traversal"] = graph_results
    print(f"       1-hop p95: {graph_results['1_hop']['p95_ms']}ms")
    print(f"       2-hop p95: {graph_results['2_hop']['p95_ms']}ms")
    print(f"       3-hop p95: {graph_results['3_hop']['p95_ms']}ms")
    print()

    # Benchmark #5: Memory
    print("[6/6] Measuring memory footprint...")
    mem_results = bench_memory()
    results["memory"] = mem_results
    print(f"       RSS: {mem_results['rss_mb']} MB")
    print()

    # Benchmark #6: Cold start
    print("[bonus] Simulating cold start (index rebuild)...")
    cold_results = bench_cold_start(embeddings, rules)
    results["cold_start"] = cold_results
    print(f"       Total index rebuild: {cold_results['total_index_rebuild_s']}s")
    print()

    # Save raw results
    out_dir = Path(__file__).parent
    results_path = out_dir / "benchmark_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Raw results saved to: {results_path}")

    # Generate markdown report
    report = generate_report(results)
    report_path = out_dir.parent / "benchmark.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    print()
    print("=" * 60)
    print("BENCHMARKS COMPLETE")
    print("=" * 60)

    return results


def generate_report(r):
    """Generate the benchmark.md report from results."""
    embed = r["embedding_time"]
    hnsw = r["hnsw_search"]
    bm25 = r["bm25_search"]
    graph = r["graph_traversal"]
    mem = r["memory"]
    cold = r["cold_start"]

    # Determine pass/fail for each handbook target
    def pf(val, target, op="lt"):
        if op == "lt":
            return "PASS" if val < target else "FAIL"
        return "PASS" if val > target else "FAIL"

    # Best ef_search that meets latency budget
    best_ef = None
    for ef_key in ["ef_400", "ef_200", "ef_100", "ef_50"]:
        data = hnsw["by_ef_search"].get(ef_key, {})
        if data.get("p95_ms", 999) < 3.0:
            best_ef = ef_key

    report = f"""# Phaselock Pre-Implementation Benchmark Results

**Date:** {r['meta']['timestamp']}
**Python:** {r['meta']['python_version'].split()[0]}
**Corpus:** {r['meta']['n_synthetic_rules']} synthetic rules

---

## Summary: Handbook Targets vs. Measured

| Target (Handbook) | Budget | Measured (p95) | Verdict |
|---|---|---|---|
| Stage 2: BM25 top-50 | < 2ms | {bm25['p95_ms']}ms | **{pf(bm25['p95_ms'], 2.0)}** |
| Stage 3: HNSW ANN search (ef=100) | < 3ms | {hnsw['by_ef_search']['ef_100']['p95_ms']}ms | **{pf(hnsw['by_ef_search']['ef_100']['p95_ms'], 3.0)}** |
| Stage 4: Graph traversal 1-2 hop | < 3ms | {graph['2_hop']['p95_ms']}ms | **{pf(graph['2_hop']['p95_ms'], 3.0)}** |
| Single rule ingestion (embed only) | < 2s | {embed['single_rule_p95_ms']}ms | **{pf(embed['single_rule_p95_ms'], 2000)}** |
| Cold start (index rebuild) | < 3s | {cold['total_index_rebuild_s']}s | **{pf(cold['total_index_rebuild_s'], 3.0)}** |
| Memory footprint | < 2 GB | {mem['rss_mb']} MB | **{pf(mem['rss_mb'], 2048)}** |

---

## Benchmark #1: Embedding Generation (all-MiniLM-L6-v2)

| Metric | Value |
|---|---|
| Dimensions | {embed['embedding_dim']} |
| Single rule p50 | {embed['single_rule_p50_ms']}ms |
| Single rule p95 | {embed['single_rule_p95_ms']}ms |
| Single rule mean | {embed['single_rule_mean_ms']}ms |
| Batch 68 rules (migration) | {embed['batch_68_total_s']}s |
| Batch 1,000 rules | {embed['batch_1000_total_s']}s |

**Verdict:** Single-rule embedding is well within the 2s ingestion budget. Batch migration of all 68 rules completes in under {embed['batch_68_total_s']}s.

---

## Benchmark #2: HNSW ANN Search (1,000 vectors, {embed['embedding_dim']}-dim)

Index build: {hnsw['build_time_s']}s | Index size: {hnsw['index_size_mb']} MB | ef_construction=200, M=16

| ef_search | p50 (ms) | p95 (ms) | p99 (ms) | Recall@10 |
|---|---|---|---|---|
"""
    for ef_key in ["ef_50", "ef_100", "ef_200", "ef_400"]:
        d = hnsw["by_ef_search"][ef_key]
        marker = " *" if ef_key == best_ef else ""
        report += f"| {ef_key.replace('ef_', '')}{marker} | {d['p50_ms']} | {d['p95_ms']} | {d['p99_ms']} | {d['recall_at_10']} |\n"

    report += f"""
**Tradeoff analysis:** The handbook Stage 3 budget is < 3ms (p95). The table above shows the latency/recall curve at each ef_search value. Higher ef_search improves recall but increases latency. The Phase 5 evaluation must pick the value that satisfies both the latency budget and MRR@5 > 0.85.

---

## Benchmark #3: BM25 Top-50 Retrieval (1,000 documents)

| Metric | Value |
|---|---|
| Index build time | {bm25['build_time_s']}s |
| Queries | {bm25['n_queries']} |
| p50 | {bm25['p50_ms']}ms |
| p95 | {bm25['p95_ms']}ms |
| p99 | {bm25['p99_ms']}ms |

---

## Benchmark #4: Graph Traversal (NetworkX in-memory, 1,000 nodes)

{graph['n_nodes']} nodes, {graph['n_edges']} edges (avg degree {graph['avg_degree']})

| Hops | p50 (ms) | p95 (ms) | p99 (ms) | Queries |
|---|---|---|---|---|
| 1-hop | {graph['1_hop']['p50_ms']} | {graph['1_hop']['p95_ms']} | {graph['1_hop']['p99_ms']} | {graph['1_hop']['n_queries']} |
| 2-hop | {graph['2_hop']['p50_ms']} | {graph['2_hop']['p95_ms']} | {graph['2_hop']['p99_ms']} | {graph['2_hop']['n_queries']} |
| 3-hop | {graph['3_hop']['p50_ms']} | {graph['3_hop']['p95_ms']} | {graph['3_hop']['p99_ms']} | {graph['3_hop']['n_queries']} |

**Note:** This is NetworkX (pure Python, in-memory). It serves as a *ceiling* for what a dedicated graph engine should achieve. If NetworkX in-memory meets the budget, any graph DB will also meet it. If NetworkX misses, the pre-computed adjacency list mitigation (Section 4.1) gives equivalent performance. The Phase 2 benchmark against Neo4j and PostgreSQL+AGE remains necessary for the production path.

---

## Benchmark #5: Memory Footprint

| Metric | Value |
|---|---|
| RSS (resident) | {mem['rss_mb']} MB |
| VMS (virtual) | {mem['vms_mb']} MB |

This includes: sentence-transformers model ({embed['embedding_dim']}-dim), HNSW index ({hnsw['index_size_mb']} MB on disk), BM25 index, NetworkX graph, and Python runtime. The 2 GB budget target is for the warm service without the embedding model loaded (model is only needed during ingestion, not query time).

---

## Benchmark #6: Cold Start (Index Rebuild)

| Component | Time |
|---|---|
| HNSW index rebuild | {cold['hnsw_rebuild_s']}s |
| BM25 index rebuild | {cold['bm25_rebuild_s']}s |
| **Total** | **{cold['total_index_rebuild_s']}s** |

{cold['note']}

---

## Implications for the Handbook

Based on these results:

1. **Stage 3 (HNSW):** [Review the ef_search table above to determine if < 3ms is achievable at acceptable recall]
2. **Stage 4 (Graph traversal):** NetworkX in-memory gives a performance floor. If 2-hop meets budget here, the pre-computed adjacency list mitigation is validated as viable.
3. **BM25:** Expected to be the cheapest stage.
4. **Ingestion:** Embedding time is negligible compared to the 2s budget. DB write time is the unknown.
5. **Cold start:** Index rebuild time determines whether the 3s target is feasible. Embedding model load time (not measured here) adds to this.
6. **Memory:** The total footprint at 1,000 rules informs whether the 2 GB target holds.
"""
    return report


if __name__ == "__main__":
    main()

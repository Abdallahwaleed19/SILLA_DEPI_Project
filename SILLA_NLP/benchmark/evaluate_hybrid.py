"""
SILLA_NLP/benchmark/evaluate_hybrid.py
======================================
Comprehensive Comparative Benchmark Suite:
Evaluates TF-IDF Baseline, Sentence Transformers Baseline, and Hybrid NLP Engine
across Precision@1, Precision@3, Recall@3, MRR, Rejection Accuracy, and Latency.
"""

import json
import time
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_NLP.config.settings import (
    STAGING_DB_PATH,
    BENCHMARK_REPORT_PATH
)
from SILLA_NLP.preprocessing.query_preprocessor import (
    preprocess_query_bundle,
    clean_query_text
)
from SILLA_NLP.matching.sparse_engine import SparseEngine
from SILLA_NLP.matching.dense_engine import DenseEngine
from SILLA_NLP.matching.hybrid_engine import HybridEngine

# ---------------------------------------------------------------------------
# Independent Validation Set (for Hyperparameter & Threshold Calibration)
# ---------------------------------------------------------------------------
VALIDATION_SET = [
    {"qid": "VAL-01", "query": "طريقة عمل الفتة بالخل والتوم", "relevant": ["R0005"], "type": "in_catalog"},
    {"qid": "VAL-02", "query": "chicken breast with rice", "relevant": ["R0015"], "type": "in_catalog"},
    {"qid": "VAL-03", "query": "محشي مشكل كوسة وباذنجان", "relevant": ["R0004"], "type": "in_catalog"},
    {"qid": "VAL-04", "query": "وجبة اقتصادية بدون لحوم", "relevant": ["R0002", "R0008", "R0010", "R0011", "R0016"], "type": "broad"},
    {"qid": "VAL-05", "query": "homemade pizza dough", "relevant": ["R0014"], "type": "in_catalog"},
    {"qid": "VAL-06", "query": "أكلات باللحمة المفرومة", "relevant": ["R0001", "R0006", "R0007", "R0013"], "type": "broad"},
    {"qid": "VAL-07", "query": "طبق جانبي خفيف", "relevant": ["R0016"], "type": "broad"},
    {"qid": "VAL-08", "query": "fettuccine with white sauce", "relevant": ["R0012"], "type": "in_catalog"},
    {"qid": "VAL-09", "query": "شاورما لحمة مصري", "relevant": [], "type": "out_of_catalog"},
    {"qid": "VAL-10", "query": "تشيز كيك بالتوت", "relevant": [], "type": "out_of_catalog"},
]

# ---------------------------------------------------------------------------
# Core Benchmark Test Set (SMK-01 to SMK-16) + Dialect Stress (SMK-17 to SMK-20)
# ---------------------------------------------------------------------------
BENCHMARK_SET = [
    # 1. In-Catalog Standard Queries
    {"qid": "SMK-01", "category": "In-Catalog", "query": "كشري مصري", "relevant": ["R0002"]},
    {"qid": "SMK-02", "category": "In-Catalog", "query": "مكرونة بشاميل باللحمة", "relevant": ["R0001"]},
    {"qid": "SMK-03", "category": "In-Catalog", "query": "شوربة عدس بالشعرية", "relevant": ["R0008"]},
    {"qid": "SMK-04", "category": "In-Catalog", "query": "Egyptian fattah with meat", "relevant": ["R0005"]},
    {"qid": "SMK-05", "category": "In-Catalog", "query": "pasta with chicken and cream", "relevant": ["R0012"]},

    # 2. Ambiguous & Broad Queries
    {"qid": "SMK-06", "category": "Ambiguous/Broad", "query": "أكلة سريعة بالبيض", "relevant": ["R0009"]},
    {"qid": "SMK-07", "category": "Ambiguous/Broad", "query": "شوربة خضار صحية", "relevant": ["R0016"]},
    {"qid": "SMK-08", "category": "Ambiguous/Broad", "query": "Italian pasta dish", "relevant": ["R0001", "R0012", "R0013"]},

    # 3. Egyptian Colloquial Queries
    {"qid": "SMK-09", "category": "Colloquial", "query": "عايز اعمل حواوشي في العيش البلدي", "relevant": ["R0006"]},
    {"qid": "SMK-10", "category": "Colloquial", "query": "فطار مصري فول وطعمية", "relevant": ["R0010", "R0011"]},
    {"qid": "SMK-11", "category": "Colloquial", "query": "كفتة مشوية على الفحم زي المحلات", "relevant": ["R0007"]},
    {"qid": "SMK-12", "category": "Colloquial", "query": "ملوخية خضرا بالطشة", "relevant": ["R0003"]},

    # 4. Out-of-Catalog & Non-Food Rejection Tests
    {"qid": "SMK-13", "category": "Out-of-Catalog", "query": "شاحن موبايل تايب سي سريع", "relevant": []},
    {"qid": "SMK-14", "category": "Out-of-Catalog", "query": "سوشي ياباني سلمون وأرز", "relevant": []},
    {"qid": "SMK-15", "category": "Out-of-Catalog", "query": "تشيز كيك شوكولاتة وحلويات غربية", "relevant": []},
    {"qid": "SMK-16", "category": "Out-of-Catalog", "query": "ساندوتش برجر بيج ماك بالجبنة", "relevant": []},

    # 5. Extended Egyptian Dialect & Synonym Stress Tests
    {"qid": "SMK-17", "category": "Colloquial-Extended", "query": "صينية فراخ بالبطاطس في الفرن", "relevant": ["R0042", "R0030", "R0015", "R0162"]},
    {"qid": "SMK-18", "category": "Colloquial-Extended", "query": "طريقة عمل البيتزا في البيت بعجينة هشة", "relevant": ["R0014"]},
    {"qid": "SMK-19", "category": "Ambiguous-Reject", "query": "أكل سريع وخلاص", "relevant": []},
    {"qid": "SMK-20", "category": "Out-of-Catalog", "query": "كابل شاحن لابتوب ديل اصلي", "relevant": []},
]


def evaluate_system(search_fn, system_name: str, threshold: float = 0.0) -> Dict[str, Any]:
    """Evaluate a search function over BENCHMARK_SET."""
    query_details = []
    p1_list, p3_list, r3_list, mrr_list = [], [], [], []
    latencies = []
    
    correct_rejections = 0
    total_rejections = 0
    false_acceptances = 0
    false_rejections = 0

    for item in BENCHMARK_SET:
        qid = item["qid"]
        category = item["category"]
        query = item["query"]
        relevant = item["relevant"]
        is_negative = (len(relevant) == 0)

        t0 = time.time()
        res = search_fn(query)
        latency_ms = (time.time() - t0) * 1000.0
        latencies.append(latency_ms)

        retrieved_ids = res["retrieved_ids"]
        scores = res["scores"]
        status = res.get("status", "SEARCH_DONE")
        guard_decision = res.get("guard_decision", "N/A")

        if is_negative:
            total_rejections += 1
            if len(retrieved_ids) == 0:
                correct_rejections += 1
                q_status = "CORRECT_REJECTION"
            else:
                false_acceptances += 1
                q_status = f"FALSE_ACCEPTANCE (retrieved: {retrieved_ids[:3]})"
            p1, p3, r3, mrr = 0.0, 0.0, 0.0, 0.0
        else:
            if len(retrieved_ids) == 0:
                false_rejections += 1
                q_status = "FALSE_REJECTION (empty)"
                p1, p3, r3, mrr = 0.0, 0.0, 0.0, 0.0
            else:
                p1 = 1.0 if retrieved_ids[0] in relevant else 0.0
                tp3 = len(set(retrieved_ids[:3]) & set(relevant))
                p3 = tp3 / 3.0
                r3 = tp3 / len(relevant)

                mrr = 0.0
                for rank, rid in enumerate(retrieved_ids[:3], start=1):
                    if rid in relevant:
                        mrr = 1.0 / rank
                        break

                q_status = f"HIT (P@1={p1:.1f}, P@3={p3:.2f}, R@3={r3:.2f}, MRR={mrr:.2f})"

            p1_list.append(p1)
            p3_list.append(p3)
            r3_list.append(r3)
            mrr_list.append(mrr)

        query_details.append({
            "qid": qid,
            "category": category,
            "query": query,
            "relevant": relevant,
            "retrieved": retrieved_ids[:3],
            "scores": scores[:3],
            "status": q_status,
            "guard_decision": guard_decision,
            "latency_ms": round(latency_ms, 2)
        })

    in_catalog_count = len(p1_list)
    rejection_rate = (correct_rejections / total_rejections) if total_rejections > 0 else 1.0

    return {
        "system": system_name,
        "threshold": threshold,
        "mean_precision_at_1": round(float(np.mean(p1_list)), 4) if p1_list else 0.0,
        "mean_precision_at_3": round(float(np.mean(p3_list)), 4) if p3_list else 0.0,
        "mean_recall_at_3": round(float(np.mean(r3_list)), 4) if r3_list else 0.0,
        "mean_mrr": round(float(np.mean(mrr_list)), 4) if mrr_list else 0.0,
        "out_of_catalog_rejection_rate": round(float(rejection_rate), 4),
        "false_acceptance_count": false_acceptances,
        "false_rejection_count": false_rejections,
        "average_latency_ms": round(float(np.mean(latencies)), 2),
        "query_results": query_details
    }


def run_benchmark():
    print("=" * 70)
    print("SILLA NLP COMPREHENSIVE BENCHMARK: TF-IDF vs SENTENCE TRANSFORMERS vs HYBRID")
    print(f"Data Source: {STAGING_DB_PATH}")
    print("=" * 70)

    # 1. Initialize Engines
    print("\n[1/4] Initializing Retrieval Engines ...")
    sparse_eng = SparseEngine(STAGING_DB_PATH)
    dense_eng = DenseEngine(STAGING_DB_PATH)
    hybrid_eng = HybridEngine(STAGING_DB_PATH)

    # 2. Benchmark Pure TF-IDF Baseline (with threshold 0.23 from previous tuning)
    print("\n[2/4] Benchmarking Pure TF-IDF Baseline ...")
    tfidf_tau = 0.23

    def tfidf_search(query: str):
        clean_q = clean_query_text(query)
        raw_res = sparse_eng.search(clean_q, top_k=3)
        filtered = [(rid, score) for rid, score in raw_res if score >= tfidf_tau]
        return {
            "retrieved_ids": [r[0] for r in filtered],
            "scores": [round(r[1], 4) for r in filtered],
            "guard_decision": "NO_GUARD"
        }

    tfidf_results = evaluate_system(tfidf_search, "TF-IDF (Scikit-Learn Baseline)", tfidf_tau)
    print(f"   -> TF-IDF: P@1={tfidf_results['mean_precision_at_1']:.2f}, MRR={tfidf_results['mean_mrr']:.2f}, RejRate={tfidf_results['out_of_catalog_rejection_rate']:.1%}")

    # 3. Benchmark Pure Sentence Transformers Baseline (with threshold 0.26 from previous tuning)
    print("\n[3/4] Benchmarking Pure Sentence Transformers Baseline ...")
    st_tau = 0.26

    def st_search(query: str):
        clean_q = clean_query_text(query)
        raw_res = dense_eng.search(clean_q, top_k=3)
        filtered = [(rid, score) for rid, score in raw_res if score >= st_tau]
        return {
            "retrieved_ids": [r[0] for r in filtered],
            "scores": [round(r[1], 4) for r in filtered],
            "guard_decision": "NO_GUARD"
        }

    st_results = evaluate_system(st_search, "Sentence Transformers (Dense Baseline)", st_tau)
    print(f"   -> ST:     P@1={st_results['mean_precision_at_1']:.2f}, MRR={st_results['mean_mrr']:.2f}, RejRate={st_results['out_of_catalog_rejection_rate']:.1%}")

    # 4. Benchmark SILLA Hybrid Engine
    print("\n[4/4] Benchmarking SILLA Hybrid NLP Engine ...")
    hybrid_tau = 0.18

    def hybrid_search(query: str):
        res = hybrid_eng.search(query, top_k=3, threshold=hybrid_tau)
        if not res["is_valid"]:
            return {
                "retrieved_ids": [],
                "scores": [],
                "guard_decision": res["guard_decision"]
            }
        return {
            "retrieved_ids": [r["recipe_id"] for r in res["results"]],
            "scores": [r["hybrid_score"] for r in res["results"]],
            "guard_decision": res["guard_decision"]
        }

    hybrid_results = evaluate_system(hybrid_search, "SILLA Hybrid NLP Engine (Sparse + Dense + Guard + Colloquial)", hybrid_tau)
    print(f"   -> Hybrid: P@1={hybrid_results['mean_precision_at_1']:.2f}, MRR={hybrid_results['mean_mrr']:.2f}, RejRate={hybrid_results['out_of_catalog_rejection_rate']:.1%}")

    # 5. Compile Final Comparison Report
    final_report = {
        "benchmark_metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "database_source": str(STAGING_DB_PATH),
            "total_queries_evaluated": len(BENCHMARK_SET),
            "in_catalog_queries": len([q for q in BENCHMARK_SET if len(q["relevant"]) > 0]),
            "negative_rejection_queries": len([q for q in BENCHMARK_SET if len(q["relevant"]) == 0])
        },
        "comparative_summary": {
            "systems": [
                {
                    "name": tfidf_results["system"],
                    "threshold": tfidf_results["threshold"],
                    "precision_at_1": tfidf_results["mean_precision_at_1"],
                    "precision_at_3": tfidf_results["mean_precision_at_3"],
                    "recall_at_3": tfidf_results["mean_recall_at_3"],
                    "mrr": tfidf_results["mean_mrr"],
                    "out_of_catalog_rejection_rate": tfidf_results["out_of_catalog_rejection_rate"],
                    "false_acceptances": tfidf_results["false_acceptance_count"],
                    "false_rejections": tfidf_results["false_rejection_count"],
                    "avg_latency_ms": tfidf_results["average_latency_ms"]
                },
                {
                    "name": st_results["system"],
                    "threshold": st_results["threshold"],
                    "precision_at_1": st_results["mean_precision_at_1"],
                    "precision_at_3": st_results["mean_precision_at_3"],
                    "recall_at_3": st_results["mean_recall_at_3"],
                    "mrr": st_results["mean_mrr"],
                    "out_of_catalog_rejection_rate": st_results["out_of_catalog_rejection_rate"],
                    "false_acceptances": st_results["false_acceptance_count"],
                    "false_rejections": st_results["false_rejection_count"],
                    "avg_latency_ms": st_results["average_latency_ms"]
                },
                {
                    "name": hybrid_results["system"],
                    "threshold": hybrid_results["threshold"],
                    "precision_at_1": hybrid_results["mean_precision_at_1"],
                    "precision_at_3": hybrid_results["mean_precision_at_3"],
                    "recall_at_3": hybrid_results["mean_recall_at_3"],
                    "mrr": hybrid_results["mean_mrr"],
                    "out_of_catalog_rejection_rate": hybrid_results["out_of_catalog_rejection_rate"],
                    "false_acceptances": hybrid_results["false_acceptance_count"],
                    "false_rejections": hybrid_results["false_rejection_count"],
                    "avg_latency_ms": hybrid_results["average_latency_ms"]
                }
            ]
        },
        "tfidf_baseline_details": tfidf_results,
        "dense_baseline_details": st_results,
        "hybrid_engine_details": hybrid_results
    }

    BENCHMARK_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BENCHMARK_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Benchmark Report successfully exported to: {BENCHMARK_REPORT_PATH}")
    return final_report


if __name__ == "__main__":
    run_benchmark()

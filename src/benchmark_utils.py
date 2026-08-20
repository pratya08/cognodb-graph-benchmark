import time
import statistics
import json
import os


WARMUP_RUNS = 10
BENCHMARK_RUNS = 100


def percentile(values, p):
    """
    Calculate percentile using linear interpolation.
    """
    if not values:
        return None

    values = sorted(values)

    k = (len(values) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(values) - 1)

    if f == c:
        return values[f]

    return values[f] + (values[c] - values[f]) * (k - f)


def benchmark_query(query_function, warmup=WARMUP_RUNS, runs=BENCHMARK_RUNS):
    """
    Execute a query repeatedly and measure latency in milliseconds.

    Warm-up executions are NOT included in the reported results.
    """

    # Warm-up
    for _ in range(warmup):
        query_function()

    latencies = []

    # Actual benchmark
    for _ in range(runs):
        start = time.perf_counter()

        query_function()

        end = time.perf_counter()

        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)

    return {
        "runs": runs,
        "p50_ms": percentile(latencies, 50),
        "p95_ms": percentile(latencies, 95),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": statistics.mean(latencies),
    }


def save_result(database, workload, result, filename="results/raw/benchmark_results.json"):
    """
    Save benchmark result to a JSON file.
    """

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    data = []

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

    data.append({
        "database": database,
        "workload": workload,
        **result
    })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print()
    print("=" * 50)
    print(f"Database : {database}")
    print(f"Workload : {workload}")
    print(f"Runs     : {result['runs']}")
    print(f"P50      : {result['p50_ms']:.3f} ms")
    print(f"P95      : {result['p95_ms']:.3f} ms")
    print(f"Min      : {result['min_ms']:.3f} ms")
    print(f"Max      : {result['max_ms']:.3f} ms")
    print(f"Mean     : {result['mean_ms']:.3f} ms")
    print("=" * 50)


if __name__ == "__main__":
    print("Benchmark utilities loaded successfully.")
    print(f"Warm-up runs : {WARMUP_RUNS}")
    print(f"Benchmark runs: {BENCHMARK_RUNS}")

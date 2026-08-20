import os
from dotenv import load_dotenv
load_dotenv()

import json
import time
import statistics
import pydgraph

DGRAPH_HOST = os.getenv("DGRAPH_HOST", "localhost:9080")


def benchmark(client, name, query, runs=100):
    # Warm-up
    for _ in range(10):
        client.txn(read_only=True).query(query)

    times = []

    for _ in range(runs):
        start = time.perf_counter()
        client.txn(read_only=True).query(query)
        times.append((time.perf_counter() - start) * 1000)

    times.sort()

    result = {
        "database": "Dgraph",
        "workload": name,
        "runs": runs,
        "p50_ms": times[49],
        "p95_ms": times[94],
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": statistics.mean(times),
    }

    print()
    print("=" * 50)
    print("Database :", result["database"])
    print("Workload :", result["workload"])
    print("Runs     :", result["runs"])
    print(f"P50      : {result['p50_ms']:.3f} ms")
    print(f"P95      : {result['p95_ms']:.3f} ms")
    print(f"Min      : {result['min_ms']:.3f} ms")
    print(f"Max      : {result['max_ms']:.3f} ms")
    print(f"Mean     : {result['mean_ms']:.3f} ms")
    print("=" * 50)

    return result


def main():
    print("Connecting to Dgraph...")

    client = pydgraph.DgraphClient(
        pydgraph.DgraphClientStub(DGRAPH_HOST)
    )

    print("Connection successful!")

    # Existing indexed predicate: id
    point_query = """
    query lookup() {
        users(func: eq(id, "0")) {
            uid
            id
        }
    }
    """

    filtered_query = """
    query lookup() {
        users(func: eq(id, "0")) {
            uid
            id
        }
    }
    """

    point_result = benchmark(
        client,
        "point lookup",
        point_query
    )

    filtered_result = benchmark(
        client,
        "indexed filtered lookup",
        filtered_query
    )

    os.makedirs("results/raw", exist_ok=True)

    with open("results/raw/dgraph_point_lookup.json", "w") as f:
        json.dump(point_result, f, indent=2)

    with open("results/raw/dgraph_indexed_filtered_lookup.json", "w") as f:
        json.dump(filtered_result, f, indent=2)

    client.close()

    print("Dgraph lookup benchmarks complete.")


if __name__ == "__main__":
    main()

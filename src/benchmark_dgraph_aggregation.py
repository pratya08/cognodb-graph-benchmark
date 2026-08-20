import os
from dotenv import load_dotenv
load_dotenv()

import json
import time
import statistics
import pydgraph

DGRAPH_HOST = os.getenv("DGRAPH_HOST", "localhost:9080")


def main():
    client = pydgraph.DgraphClient(
        pydgraph.DgraphClientStub(DGRAPH_HOST)
    )

    print("Connecting to Dgraph...")
    print("Connection successful!")

    query = """
    query aggregation() {
        users(func: has(id)) {
            uid
        }
    }
    """

    # Warm-up
    for _ in range(10):
        client.txn(read_only=True).query(query)

    timings = []

    for _ in range(100):
        start = time.perf_counter()
        response = client.txn(read_only=True).query(query)
        elapsed = (time.perf_counter() - start) * 1000
        timings.append(elapsed)

    timings.sort()

    result = {
        "database": "Dgraph",
        "workload": "aggregation",
        "runs": 100,
        "p50_ms": timings[49],
        "p95_ms": timings[94],
        "min_ms": min(timings),
        "max_ms": max(timings),
        "mean_ms": statistics.mean(timings)
    }

    print()
    print("=" * 50)
    print("Database : Dgraph")
    print("Workload : aggregation")
    print("Runs     : 100")
    print(f"P50      : {result['p50_ms']:.3f} ms")
    print(f"P95      : {result['p95_ms']:.3f} ms")
    print(f"Min      : {result['min_ms']:.3f} ms")
    print(f"Max      : {result['max_ms']:.3f} ms")
    print(f"Mean     : {result['mean_ms']:.3f} ms")
    print("=" * 50)

    os.makedirs("results/raw", exist_ok=True)

    with open("results/raw/dgraph_aggregation.json", "w") as f:
        json.dump(result, f, indent=2)

    client.close()

    print("Dgraph aggregation benchmark complete.")


if __name__ == "__main__":
    main()

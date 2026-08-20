import os
from dotenv import load_dotenv
load_dotenv()

import json
import random
import time
import statistics

import pydgraph


DGRAPH_ADDRESS = os.getenv("DGRAPH_HOST", "localhost:9080")
RUNS = 100
WARMUP = 10
STARTING_NODES = 1000


def save_result(workload, times):
    result = {
        "database": "Dgraph",
        "workload": workload,
        "runs": len(times),
        "p50_ms": statistics.median(times),
        "p95_ms": sorted(times)[int(0.95 * len(times)) - 1],
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": statistics.mean(times),
    }

    filename = workload.replace("-", "_").replace(" ", "_")
    path = f"results/dgraph_{filename}.json"

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    print()
    print("=" * 55)
    print(f"Database : Dgraph")
    print(f"Workload : {workload}")
    print("=" * 55)
    print(f"Runs     : {result['runs']}")
    print(f"P50      : {result['p50_ms']:.3f} ms")
    print(f"P95      : {result['p95_ms']:.3f} ms")
    print(f"Min      : {result['min_ms']:.3f} ms")
    print(f"Max      : {result['max_ms']:.3f} ms")
    print(f"Mean     : {result['mean_ms']:.3f} ms")


def main():
    print("Connecting to Dgraph...")

    stub = pydgraph.DgraphClientStub(DGRAPH_ADDRESS)
    client = pydgraph.DgraphClient(stub)

    print("Connection successful!")

    # ---------------------------------------------------------
    # Get starting users.
    # This setup is NOT part of the timed benchmark.
    # ---------------------------------------------------------
    query = """
    {
        users(func: has(id), first: 1000) {
            id
        }
    }
    """

    response = client.txn(read_only=True).query(query)

    import json as json_parser
    users = json_parser.loads(response.json).get("users", [])
    start_nodes = [user["id"] for user in users]

    if not start_nodes:
        stub.close()
        raise RuntimeError("No User nodes found in Dgraph.")

    print(f"Starting nodes available: {len(start_nodes)}")

    # Use one fixed starting node for all benchmark iterations,
    # matching the methodology used in the other benchmarks.
    start_id = random.choice(start_nodes)

    print(f"Benchmark starting node: {start_id}")

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    queries = {
        "1-hop traversal": f'''
        {{
            user(func: eq(id, "{start_id}")) {{
                uid
                TRUSTS {{
                    uid
                }}
            }}
        }}
        ''',

        "2-hop traversal": f'''
        {{
            user(func: eq(id, "{start_id}")) {{
                uid
                TRUSTS {{
                    uid
                    TRUSTS {{
                        uid
                    }}
                }}
            }}
        }}
        ''',

        "3-hop traversal": f'''
        {{
            user(func: eq(id, "{start_id}")) {{
                uid
                TRUSTS {{
                    uid
                    TRUSTS {{
                        uid
                        TRUSTS {{
                            uid
                        }}
                    }}
                }}
            }}
        }}
        '''
    }

    # ---------------------------------------------------------
    # Run all three workloads
    # ---------------------------------------------------------

    for workload, query in queries.items():

        print()
        print(f"Running Dgraph {workload} benchmark...")
        print(f"Warm-up: {WARMUP} runs")
        print(f"Measured: {RUNS} runs")

        # Warm-up
        for _ in range(WARMUP):
            txn = client.txn(read_only=True)
            try:
                txn.query(query)
            finally:
                txn.discard()

        # Measured runs
        times = []

        for _ in range(RUNS):
            txn = client.txn(read_only=True)

            try:
                start = time.perf_counter()
                txn.query(query)
                end = time.perf_counter()

                elapsed_ms = (end - start) * 1000
                times.append(elapsed_ms)

            finally:
                txn.discard()

        save_result(workload, times)

    stub.close()

    print()
    print("=" * 55)
    print("Dgraph 1-hop + 2-hop + 3-hop benchmark complete.")
    print("=" * 55)


if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv
load_dotenv()

import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import pydgraph

DGRAPH_HOST = os.getenv("DGRAPH_HOST", "localhost:9080")


def main():
    client = pydgraph.DgraphClient(
        pydgraph.DgraphClientStub(DGRAPH_HOST)
    )

    print("Connecting to Dgraph...")
    print("Connection successful!")

    # Read: 1-hop TRUSTS traversal from a random user.
    read_query = """
    query read($id: string) {
        users(func: eq(id, $id)) {
            trusts {
                uid
                id
            }
        }
    }
    """

    # Get a real user ID from the database.
    response = client.txn(read_only=True).query("""
    {
        users(func: has(id), first: 100) {
            id
        }
    }
    """)

    data = json.loads(response.json)
    users = data.get("users", [])

    if not users:
        raise RuntimeError("No users with id found in Dgraph.")

    user_ids = [u["id"] for u in users]

    def read_operation():
        user_id = random.choice(user_ids)
        client.txn(read_only=True).query(
            read_query,
            variables={"$id": user_id}
        )

    def write_operation():
        user_id = random.choice(user_ids)

        response = client.txn(read_only=True).query(
            """
            query getUser($id: string) {
                users(func: eq(id, $id)) {
                    uid
                }
            }
            """,
            variables={"$id": user_id}
        )

        data = json.loads(response.json)
        users = data.get("users", [])

        if not users:
            return

        uid = users[0]["uid"]

        txn = client.txn()
        try:
            mutation = pydgraph.Mutation(
                set_nquads=f'<{uid}> <benchmark_value> "{random.randint(1, 1000000)}" .'.encode()
            )
            txn.mutate(mutation=mutation)
            txn.commit()
        finally:
            txn.discard()

    def mixed_run():
        start = time.perf_counter()

        with ThreadPoolExecutor(max_workers=2) as executor:
            read_future = executor.submit(read_operation)
            write_future = executor.submit(write_operation)

            read_future.result()
            write_future.result()

        return (time.perf_counter() - start) * 1000

    print("Warm-up: 10 runs")

    for _ in range(10):
        mixed_run()

    print("Measured: 100 runs")

    timings = []

    for _ in range(100):
        timings.append(mixed_run())

    timings.sort()

    result = {
        "database": "Dgraph",
        "workload": "mixed concurrent read/write",
        "runs": 100,
        "p50_ms": timings[49],
        "p95_ms": timings[94],
        "min_ms": min(timings),
        "max_ms": max(timings),
        "mean_ms": statistics.mean(timings),
    }

    print()
    print("=" * 50)
    print("Database : Dgraph")
    print("Workload : mixed concurrent read/write")
    print("Runs     : 100")
    print(f"P50      : {result['p50_ms']:.3f} ms")
    print(f"P95      : {result['p95_ms']:.3f} ms")
    print(f"Min      : {result['min_ms']:.3f} ms")
    print(f"Max      : {result['max_ms']:.3f} ms")
    print(f"Mean     : {result['mean_ms']:.3f} ms")
    print("=" * 50)

    os.makedirs("results/raw", exist_ok=True)

    with open("results/raw/dgraph_mixed.json", "w") as f:
        json.dump(result, f, indent=2)

    client.close()

    print("Dgraph mixed concurrent read/write benchmark complete.")


if __name__ == "__main__":
    main()

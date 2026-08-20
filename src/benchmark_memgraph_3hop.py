import os
import random
import json
from dotenv import load_dotenv
from gqlalchemy import Memgraph

from benchmark_utils import benchmark_query

load_dotenv()

HOST = os.getenv("MEMGRAPH_HOST")
PORT = int(os.getenv("MEMGRAPH_PORT", 7687))
USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")


def main():
    print("Connecting to Memgraph...")

    memgraph = Memgraph(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        encrypted=True
    )

    result = memgraph.execute_and_fetch(
        "RETURN 1 AS test"
    )

    print("Connection successful!")
    print(list(result))

    # Get valid starting nodes
    result = memgraph.execute_and_fetch(
        """
        MATCH (u:User)
        RETURN u.id AS id
        LIMIT 1000
        """
    )

    start_nodes = [row["id"] for row in result]

    if not start_nodes:
        raise RuntimeError("No User nodes found in Memgraph.")

    print(f"Starting nodes available: {len(start_nodes)}")

    def query():
        user_id = random.choice(start_nodes)

        result = memgraph.execute_and_fetch(
            """
            MATCH (u:User {id: $user_id})
                  -[]->()
                  -[]->(v:User)
            RETURN v.id AS id
            """,
            {"user_id": user_id}
        )

        return list(result)

    print()
    print("=" * 50)
    print("Database : Memgraph")
    print("Workload : 3-hop traversal")
    print("=" * 50)

    result = benchmark_query(query)

    os.makedirs("results", exist_ok=True)

    output = {
        "database": "Memgraph",
        "workload": "3-hop traversal",
        **result
    }

    with open(
        "results/memgraph_2hop.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 50)
    print(f"Runs  : {result['runs']}")
    print(f"P50   : {result['p50_ms']:.3f} ms")
    print(f"P95   : {result['p95_ms']:.3f} ms")
    print(f"Min   : {result['min_ms']:.3f} ms")
    print(f"Max   : {result['max_ms']:.3f} ms")
    print(f"Mean  : {result['mean_ms']:.3f} ms")
    print("=" * 50)

    print()
    print("Memgraph 3-hop benchmark complete.")


if __name__ == "__main__":
    main()

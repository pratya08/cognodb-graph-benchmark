import os
import random
import json
from dotenv import load_dotenv
from arango import ArangoClient

from benchmark_utils import benchmark_query

load_dotenv()

ARANGO_HOST = os.getenv("ARANGO_HOST")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")

DATABASE = "_system"


def main():
    print("Connecting to ArangoDB...")

    client = ArangoClient(hosts=ARANGO_HOST)

    db = client.db(
        DATABASE,
        username=ARANGO_USERNAME,
        password=ARANGO_PASSWORD
    )

    print("Connection successful!")

    # Get valid starting nodes
    cursor = db.aql.execute(
        """
        FOR u IN users
            LIMIT 1000
            RETURN u._key
        """
    )

    start_nodes = list(cursor)

    if not start_nodes:
        raise RuntimeError("No User nodes found in ArangoDB.")

    print(f"Starting nodes available: {len(start_nodes)}")

    def query():
        user_id = random.choice(start_nodes)

        cursor = db.aql.execute(
            """
            WITH users, trusts
            FOR v IN 1..1 OUTBOUND @start trusts
                RETURN v._key
            """,
            bind_vars={
                "start": f"users/{user_id}"
            }
        )

        return list(cursor)

    print()
    print("=" * 50)
    print("Database : ArangoDB")
    print("Workload : 1-hop traversal")
    print("=" * 50)

    result = benchmark_query(query)

    # Save benchmark result
    os.makedirs("results", exist_ok=True)

    output = {
        "database": "ArangoDB",
        "workload": "1-hop traversal",
        **result
    }

    with open("results/arangodb_1hop.json", "w", encoding="utf-8") as f:
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
    print("ArangoDB 1-hop benchmark complete.")


if __name__ == "__main__":
    main()

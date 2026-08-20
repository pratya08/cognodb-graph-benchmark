import os
import random

from dotenv import load_dotenv
from neo4j import GraphDatabase

from benchmark_utils import benchmark_query, save_result


load_dotenv()


def main():
    print("Connecting to CognoDB...")

    uri = os.getenv("COGNODB_URI")
    username = os.getenv("COGNODB_USER")
    password = os.getenv("COGNODB_PASSWORD")

    if not uri or not username or not password:
        raise RuntimeError(
            "COGNODB_URI, COGNODB_USER or COGNODB_PASSWORD is missing from .env"
        )

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    driver.verify_connectivity()

    print("Connection successful!")

    # ---------------------------------------------------------
    # Get 1000 valid starting users.
    # This is setup only and is NOT part of the timed benchmark.
    # ---------------------------------------------------------

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)
            RETURN u.id AS id
            LIMIT 1000
            """
        )

        start_nodes = [record["id"] for record in result]

    if not start_nodes:
        driver.close()
        raise RuntimeError("No User nodes found in CognoDB.")

    print(f"Found {len(start_nodes)} starting nodes.")

    # Fixed random starting node so all 100 benchmark iterations
    # use the same logical lookup.
    start_id = random.choice(start_nodes)

    print(f"Benchmark starting node: {start_id}")

    # ---------------------------------------------------------
    # 1-HOP TRAVERSAL
    # ---------------------------------------------------------

    def one_hop_query():
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $start_id})-[:TRUSTS]->(v:User)
                RETURN v.id AS id
                """,
                start_id=start_id
            )

            # Consume the complete result.
            result.consume()

    print()
    print("Running 1-hop traversal benchmark...")
    print("Warm-up: 10 runs")
    print("Measured: 100 runs")

    benchmark_result = benchmark_query(one_hop_query)

    save_result(
        database="CognoDB",
        workload="1-hop traversal",
        result=benchmark_result
    )

    driver.close()

    print()
    print("CognoDB 1-hop benchmark complete.")


if __name__ == "__main__":
    main()

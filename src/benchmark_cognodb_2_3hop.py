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
    # GET 1000 VALID STARTING USERS
    # This setup is NOT part of the timed benchmark.
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

    # Fixed random starting node so both workloads
    # use the same logical starting point.
    start_id = random.choice(start_nodes)

    print(f"Benchmark starting node: {start_id}")

    # ---------------------------------------------------------
    # 2-HOP TRAVERSAL
    # ---------------------------------------------------------

    def two_hop_query():
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $start_id})
                      -[:TRUSTS]->(:User)
                      -[:TRUSTS]->(v:User)
                RETURN v.id AS id
                """,
                start_id=start_id
            )

            return list(result)

    # ---------------------------------------------------------
    # 3-HOP TRAVERSAL
    # ---------------------------------------------------------

    def three_hop_query():
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $start_id})
                      -[:TRUSTS]->(:User)
                      -[:TRUSTS]->(:User)
                      -[:TRUSTS]->(v:User)
                RETURN v.id AS id
                """,
                start_id=start_id
            )

            return list(result)

    # ---------------------------------------------------------
    # RUN 2-HOP
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("Database : CognoDB")
    print("Workload : 2-hop traversal")
    print("=" * 60)

    result_2hop = benchmark_query(two_hop_query)

    print(f"Runs  : {result_2hop['runs']}")
    print(f"P50   : {result_2hop['p50_ms']:.3f} ms")
    print(f"P95   : {result_2hop['p95_ms']:.3f} ms")
    print(f"Min   : {result_2hop['min_ms']:.3f} ms")
    print(f"Max   : {result_2hop['max_ms']:.3f} ms")
    print(f"Mean  : {result_2hop['mean_ms']:.3f} ms")

    save_result(
        database="CognoDB",
        workload="2-hop traversal",
        result=result_2hop,
        filename="results/cognodb_2hop.json"
    )

    # ---------------------------------------------------------
    # RUN 3-HOP
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("Database : CognoDB")
    print("Workload : 3-hop traversal")
    print("=" * 60)

    result_3hop = benchmark_query(three_hop_query)

    print(f"Runs  : {result_3hop['runs']}")
    print(f"P50   : {result_3hop['p50_ms']:.3f} ms")
    print(f"P95   : {result_3hop['p95_ms']:.3f} ms")
    print(f"Min   : {result_3hop['min_ms']:.3f} ms")
    print(f"Max   : {result_3hop['max_ms']:.3f} ms")
    print(f"Mean  : {result_3hop['mean_ms']:.3f} ms")

    save_result(
        database="CognoDB",
        workload="3-hop traversal",
        result=result_3hop,
        filename="results/cognodb_3hop.json"
    )

    driver.close()

    print()
    print("CognoDB 2-hop + 3-hop benchmark complete.")


if __name__ == "__main__":
    main()

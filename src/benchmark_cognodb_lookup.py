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
    # ============================================================
    # POINT + INDEXED/FILTERED LOOKUPS
    # ============================================================

    def point_lookup():
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})
                RETURN u.id AS id
                """,
                user_id=start_id
            )
            result.consume()

    def filtered_lookup():
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                WHERE u.id = $user_id
                RETURN u.id AS id
                """,
                user_id=start_id
            )
            result.consume()

    print()
    print("Running CognoDB point lookup benchmark...")
    print("Warm-up: 10 runs")
    print("Measured: 100 runs")

    point_result = benchmark_query(point_lookup)

    save_result(
        database="CognoDB",
        workload="point lookup",
        result=point_result
    )

    print()
    print("CognoDB point lookup complete.")

    print()
    print("Running CognoDB indexed/filtered lookup benchmark...")
    print("Warm-up: 10 runs")
    print("Measured: 100 runs")

    filtered_result = benchmark_query(filtered_lookup)

    save_result(
        database="CognoDB",
        workload="indexed filtered lookup",
        result=filtered_result
    )

    print()
    print("CognoDB indexed/filtered lookup complete.")

    driver.close()


if __name__ == "__main__":
    main()

import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def main():
    print("Connecting to CognoDB...")

    uri = os.getenv("COGNODB_URI")
    username = os.getenv("COGNODB_USER")
    password = os.getenv("COGNODB_PASSWORD")

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    print("Connection successful!")

    # Get valid starting user IDs.
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

    print(f"Starting nodes available: {len(start_nodes)}")

    def read_operation():
        start_id = random.choice(start_nodes)

        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $start_id})-[:TRUSTS]->(v:User)
                RETURN v.id AS id
                """,
                start_id=start_id
            )
            result.consume()

    def write_operation():
        start_id = random.choice(start_nodes)

        with driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $start_id})
                SET u.benchmark_value = $value
                """,
                start_id=start_id,
                value=random.randint(1, 1000000)
            ).consume()

    def mixed_run():
        start = time.perf_counter()

        with ThreadPoolExecutor(max_workers=2) as executor:
            read_future = executor.submit(read_operation)
            write_future = executor.submit(write_operation)

            read_future.result()
            write_future.result()

        return (time.perf_counter() - start) * 1000

    # Warm-up
    print()
    print("Running CognoDB mixed concurrent read/write benchmark...")
    print("Warm-up: 10 runs")

    for _ in range(10):
        mixed_run()

    # Measured runs
    print("Measured: 100 runs")

    timings = []

    for _ in range(100):
        timings.append(mixed_run())

    timings.sort()

    p50 = timings[49]
    p95 = timings[94]
    minimum = min(timings)
    maximum = max(timings)
    mean = sum(timings) / len(timings)

    print()
    print("=" * 50)
    print("Database : CognoDB")
    print("Workload : mixed concurrent read/write")
    print("Runs     : 100")
    print(f"P50      : {p50:.3f} ms")
    print(f"P95      : {p95:.3f} ms")
    print(f"Min      : {minimum:.3f} ms")
    print(f"Max      : {maximum:.3f} ms")
    print(f"Mean     : {mean:.3f} ms")
    print("=" * 50)

    driver.close()

    print()
    print("CognoDB mixed concurrent read/write benchmark complete.")


if __name__ == "__main__":
    main()

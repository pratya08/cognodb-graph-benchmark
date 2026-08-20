import os
import random
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

with driver.session() as session:
    records = session.run("""
        MATCH (u:User)
        RETURN u.id AS id
        LIMIT 1000
    """)
    user_ids = [r["id"] for r in records]

if not user_ids:
    raise RuntimeError("No User IDs found in Neo4j.")


def read_operation():
    user_id = random.choice(user_ids)

    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $id})-[:TRUSTS]->(v:User)
            RETURN v.id
        """, id=user_id).consume()


def write_operation():
    user_id = random.choice(user_ids)

    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $id})
            SET u.benchmark_value = $value
        """,
        id=user_id,
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


print("Running Neo4j mixed concurrent read/write benchmark...")
print("Warm-up: 10 runs")

for _ in range(10):
    mixed_run()

print("Measured: 100 runs")

timings = []

for _ in range(100):
    timings.append(mixed_run())

timings.sort()

result = {
    "database": "Neo4j",
    "workload": "mixed concurrent read/write",
    "runs": 100,
    "p50_ms": timings[49],
    "p95_ms": timings[94],
    "min_ms": min(timings),
    "max_ms": max(timings),
    "mean_ms": statistics.mean(timings)
}

print()
print("=" * 50)
print("Database : Neo4j")
print("Workload : mixed concurrent read/write")
print("Runs     : 100")
print(f"P50      : {result['p50_ms']:.3f} ms")
print(f"P95      : {result['p95_ms']:.3f} ms")
print(f"Min      : {result['min_ms']:.3f} ms")
print(f"Max      : {result['max_ms']:.3f} ms")
print(f"Mean     : {result['mean_ms']:.3f} ms")
print("=" * 50)

os.makedirs("results/raw", exist_ok=True)

with open("results/raw/neo4j_mixed.json", "w") as f:
    json.dump(result, f, indent=2)

driver.close()

print("Neo4j mixed concurrent read/write benchmark complete.")
print("Result saved to results/raw/neo4j_mixed.json")

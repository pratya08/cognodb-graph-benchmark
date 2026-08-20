import os
import random
import time
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def run_query(query, user_id):
    with driver.session() as session:
        return list(session.run(query, user_id=user_id))


def benchmark(name, query, user_ids):
    for _ in range(10):
        run_query(query, random.choice(user_ids))

    timings = []

    for _ in range(100):
        user_id = random.choice(user_ids)

        start = time.perf_counter()
        run_query(query, user_id)
        timings.append((time.perf_counter() - start) * 1000)

    timings.sort()

    result = {
        "database": "Neo4j",
        "workload": name,
        "runs": 100,
        "p50_ms": timings[49],
        "p95_ms": timings[94],
        "min_ms": min(timings),
        "max_ms": max(timings),
        "mean_ms": sum(timings) / len(timings)
    }

    print()
    print("=" * 50)
    print("Database :", result["database"])
    print("Workload :", result["workload"])
    print("Runs     :", result["runs"])
    print(f"P50      : {result['p50_ms']:.3f} ms")
    print(f"P95      : {result['p95_ms']:.3f} ms")
    print(f"Min      : {result['min_ms']:.3f} ms")
    print(f"Max      : {result['max_ms']:.3f} ms")
    print(f"Mean     : {result['mean_ms']:.3f} ms")
    print("=" * 50)

    return result


with driver.session() as session:
    records = session.run("""
        MATCH (u:User)
        RETURN u.id AS id
        LIMIT 1000
    """)
    user_ids = [r["id"] for r in records]

if not user_ids:
    raise RuntimeError("No User IDs found in Neo4j.")

point_query = """
MATCH (u:User {id: $user_id})
RETURN u.id
"""

filtered_query = """
MATCH (u:User)
WHERE u.id = $user_id
RETURN u.id
"""

point_result = benchmark(
    "point lookup",
    point_query,
    user_ids
)

filtered_result = benchmark(
    "indexed filtered lookup",
    filtered_query,
    user_ids
)

os.makedirs("results/raw", exist_ok=True)

with open("results/raw/neo4j_point_lookup.json", "w") as f:
    json.dump(point_result, f, indent=2)

with open("results/raw/neo4j_indexed_filtered_lookup.json", "w") as f:
    json.dump(filtered_result, f, indent=2)

driver.close()

print("Neo4j lookup benchmarks complete.")

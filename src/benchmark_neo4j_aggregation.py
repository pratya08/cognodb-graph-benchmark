import os
import time
import json
import statistics
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


def run_query():
    with driver.session() as session:
        return list(session.run("""
            MATCH (:User)-[:TRUSTS]->(:User)
            RETURN count(*) AS relationship_count
        """))


for _ in range(10):
    run_query()

timings = []

for _ in range(100):
    start = time.perf_counter()
    run_query()
    timings.append((time.perf_counter() - start) * 1000)

timings.sort()

result = {
    "database": "Neo4j",
    "workload": "aggregation",
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
print("Workload : aggregation")
print("Runs     : 100")
print(f"P50      : {result['p50_ms']:.3f} ms")
print(f"P95      : {result['p95_ms']:.3f} ms")
print(f"Min      : {result['min_ms']:.3f} ms")
print(f"Max      : {result['max_ms']:.3f} ms")
print(f"Mean     : {result['mean_ms']:.3f} ms")
print("=" * 50)

os.makedirs("results/raw", exist_ok=True)

with open("results/raw/neo4j_aggregation.json", "w") as f:
    json.dump(result, f, indent=2)

driver.close()

print("Neo4j aggregation benchmark complete.")

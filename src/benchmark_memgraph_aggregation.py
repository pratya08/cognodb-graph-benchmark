import os
import time
import json
import statistics

from dotenv import load_dotenv
from gqlalchemy import Memgraph

load_dotenv()

HOST = os.getenv("MEMGRAPH_HOST")
PORT = int(os.getenv("MEMGRAPH_PORT", 7687))
USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")

memgraph = Memgraph(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    encrypted=True
)

print("Connecting to Memgraph...")

list(memgraph.execute_and_fetch("RETURN 1 AS test"))

print("Connection successful!")


def run_query():
    return list(memgraph.execute_and_fetch("""
        MATCH (:User)-[:TRUSTS]->(:User)
        RETURN count(*) AS relationship_count
    """))


# Warm-up
for _ in range(10):
    run_query()

# Measured runs
timings = []

for _ in range(100):
    start = time.perf_counter()
    run_query()
    timings.append((time.perf_counter() - start) * 1000)

timings.sort()

result = {
    "database": "Memgraph",
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
print("Database : Memgraph")
print("Workload : aggregation")
print("Runs     : 100")
print(f"P50      : {result['p50_ms']:.3f} ms")
print(f"P95      : {result['p95_ms']:.3f} ms")
print(f"Min      : {result['min_ms']:.3f} ms")
print(f"Max      : {result['max_ms']:.3f} ms")
print(f"Mean     : {result['mean_ms']:.3f} ms")
print("=" * 50)

os.makedirs("results/raw", exist_ok=True)

with open("results/raw/memgraph_aggregation.json", "w") as f:
    json.dump(result, f, indent=2)

print("Memgraph aggregation benchmark complete.")

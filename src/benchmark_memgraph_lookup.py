import os
import random
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

list(memgraph.execute_and_fetch(
    "RETURN 1 AS test"
))

print("Connection successful!")

result = memgraph.execute_and_fetch("""
MATCH (u:User)
RETURN u.id AS id
LIMIT 1000
""")

user_ids = [row["id"] for row in result]

if not user_ids:
    raise RuntimeError("No User IDs found in Memgraph.")


def benchmark(name, query):
    for _ in range(10):
        list(memgraph.execute_and_fetch(
            query,
            {"id": random.choice(user_ids)}
        ))

    timings = []

    for _ in range(100):
        user_id = random.choice(user_ids)

        start = time.perf_counter()

        list(memgraph.execute_and_fetch(
            query,
            {"id": user_id}
        ))

        timings.append((time.perf_counter() - start) * 1000)

    timings.sort()

    result = {
        "database": "Memgraph",
        "workload": name,
        "runs": 100,
        "p50_ms": timings[49],
        "p95_ms": timings[94],
        "min_ms": min(timings),
        "max_ms": max(timings),
        "mean_ms": statistics.mean(timings)
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


point_query = """
MATCH (u:User {id: $id})
RETURN u.id
"""

filtered_query = """
MATCH (u:User)
WHERE u.id = $id
RETURN u.id
"""

point_result = benchmark(
    "point lookup",
    point_query
)

filtered_result = benchmark(
    "indexed filtered lookup",
    filtered_query
)

os.makedirs("results/raw", exist_ok=True)

with open("results/raw/memgraph_point_lookup.json", "w") as f:
    json.dump(point_result, f, indent=2)

with open("results/raw/memgraph_indexed_filtered_lookup.json", "w") as f:
    json.dump(filtered_result, f, indent=2)

print("Memgraph lookup benchmarks complete.")

import os
import random
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor

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

result = memgraph.execute_and_fetch("""
MATCH (u:User)
RETURN u.id AS id
LIMIT 1000
""")

user_ids = [row["id"] for row in result]

if not user_ids:
    raise RuntimeError("No User IDs found in Memgraph.")


def read_operation():
    user_id = random.choice(user_ids)

    list(memgraph.execute_and_fetch("""
        MATCH (u:User {id: $id})-[:TRUSTS]->(v:User)
        RETURN v.id
    """, {"id": user_id}))


def write_operation():
    user_id = random.choice(user_ids)

    list(memgraph.execute_and_fetch("""
        MATCH (u:User {id: $id})
        SET u.benchmark_value = $value
        RETURN u.id
    """, {
        "id": user_id,
        "value": random.randint(1, 1000000)
    }))


def mixed_run():
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=2) as executor:
        read_future = executor.submit(read_operation)
        write_future = executor.submit(write_operation)

        read_future.result()
        write_future.result()

    return (time.perf_counter() - start) * 1000


print("Running Memgraph mixed concurrent read/write benchmark...")
print("Warm-up: 10 runs")

for _ in range(10):
    mixed_run()

print("Measured: 100 runs")

timings = []

for _ in range(100):
    timings.append(mixed_run())

timings.sort()

result = {
    "database": "Memgraph",
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
print("Database : Memgraph")
print("Workload : mixed concurrent read/write")
print("Runs     : 100")
print(f"P50      : {result['p50_ms']:.3f} ms")
print(f"P95      : {result['p95_ms']:.3f} ms")
print(f"Min      : {result['min_ms']:.3f} ms")
print(f"Max      : {result['max_ms']:.3f} ms")
print(f"Mean     : {result['mean_ms']:.3f} ms")
print("=" * 50)

os.makedirs("results/raw", exist_ok=True)

with open("results/raw/memgraph_mixed.json", "w") as f:
    json.dump(result, f, indent=2)

print("Memgraph mixed concurrent read/write benchmark complete.")

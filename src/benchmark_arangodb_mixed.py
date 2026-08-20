import os
import random
import time
import json
from concurrent.futures import ThreadPoolExecutor

from arango import ArangoClient
from dotenv import load_dotenv

load_dotenv()

ARANGO_HOST = os.getenv("ARANGO_HOST")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")
ARANGO_DATABASE = os.getenv("ARANGO_DATABASE", "_system")

client = ArangoClient(hosts=ARANGO_HOST)
db = client.db(
    ARANGO_DATABASE,
    username=ARANGO_USERNAME,
    password=ARANGO_PASSWORD
)

# Get available user IDs
cursor = db.aql.execute("""
        WITH users
    FOR u IN users
            
        LIMIT 1000
        RETURN u._key
""")

start_nodes = list(cursor)

if not start_nodes:
    raise RuntimeError("No User nodes found in ArangoDB.")

print(f"Starting users available: {len(start_nodes)}")


def read_operation():
    start_id = random.choice(start_nodes)

    cursor = db.aql.execute("""
        WITH users
        FOR v IN 1..1 OUTBOUND @start
            trusts
            RETURN v._key
    """, bind_vars={
        "start": f"users/{start_id}"
    })

    list(cursor)


def write_operation():
    start_id = random.choice(start_nodes)

    db.aql.execute("""
        UPDATE @key
        WITH { benchmark_value: @value }
        IN users
            RETURN NEW
    """, bind_vars={
        "key": start_id,
        "value": random.randint(1, 1000000)
    }).next()


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
print("Running ArangoDB mixed concurrent read/write benchmark...")
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
print("Database : ArangoDB")
print("Workload : mixed concurrent read/write")
print("Runs     : 100")
print(f"P50      : {p50:.3f} ms")
print(f"P95      : {p95:.3f} ms")
print(f"Min      : {minimum:.3f} ms")
print(f"Max      : {maximum:.3f} ms")
print(f"Mean     : {mean:.3f} ms")
print("=" * 50)


# Save result
os.makedirs("results/raw", exist_ok=True)

result = {
    "database": "ArangoDB",
    "workload": "mixed concurrent read/write",
    "runs": 100,
    "p50_ms": p50,
    "p95_ms": p95,
    "min_ms": minimum,
    "max_ms": maximum,
    "mean_ms": mean
}

with open("results/raw/arangodb_mixed.json", "w") as f:
    json.dump(result, f, indent=2)

print()
print("ArangoDB mixed concurrent read/write benchmark complete.")
print("Result saved to results/raw/arangodb_mixed.json")

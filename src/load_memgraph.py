import csv
import os
import time

from dotenv import load_dotenv
from gqlalchemy import Memgraph

load_dotenv()

HOST = os.getenv("MEMGRAPH_HOST")
PORT = int(os.getenv("MEMGRAPH_PORT", 7687))
USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")

CSV_FILE = "data/processed/relationships.csv"
BATCH_SIZE = 5000

print("Connecting to Memgraph...")

memgraph = Memgraph(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    encrypted=True
)

print("Connection successful!")

start_time = time.perf_counter()

# Read CSV
with open(CSV_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print(f"Rows found: {len(rows)}")

# Clear existing graph
#memgraph.execute("MATCH (n) DETACH DELETE n")

print("keeping existing graph .")

# Load data in batches
#for i in range(0, len(rows), BATCH_SIZE):

   # batch = rows[i:i + BATCH_SIZE]
START_INDEX = 0

for i in range(START_INDEX, len(rows), BATCH_SIZE):
    batch = rows[i:i + BATCH_SIZE]
    data = [
        {
            "source": row["source"],
            "target": row["target"]
        }
        for row in batch
    ]

    memgraph.execute(
        """
        UNWIND $rows AS row

        MERGE (a:User {id: row.source})
        MERGE (b:User {id: row.target})

        MERGE (a)-[:TRUSTS]->(b)
        """,
        {"rows": data}
    )

    loaded = min(i + BATCH_SIZE, len(rows))
    print(f"Loaded {loaded}/{len(rows)}")

elapsed = time.perf_counter() - start_time

print(f"Finished loading data in {elapsed:.2f} seconds.")
import csv
import os
import time
from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()

ARANGO_HOST = os.getenv("ARANGO_HOST")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")

CSV_FILE = "data/processed/relationships.csv"
BATCH_SIZE = 5000

client = ArangoClient(hosts=ARANGO_HOST)

db = client.db(
    "_system",
    username=ARANGO_USERNAME,
    password=ARANGO_PASSWORD
)

# Create graph database collection
if not db.has_collection("users"):
    db.create_collection("users")

if not db.has_collection("trusts"):
    db.create_collection("trusts", edge=True)

users = db.collection("users")
trusts = db.collection("trusts")

print("Connected to ArangoDB.")

start = time.perf_counter()

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Rows found: {len(rows)}")

for i in range(0, len(rows), BATCH_SIZE):

    batch = rows[i:i + BATCH_SIZE]

    user_docs = {}
    edge_docs = []

    for row in batch:
        source = str(row["source"])
        target = str(row["target"])

        user_docs[source] = {
            "_key": source
        }

        user_docs[target] = {
            "_key": target
        }

        edge_docs.append({
            "_from": f"users/{source}",
            "_to": f"users/{target}"
        })

    # Ignore existing documents so the script can safely resume
    users.import_bulk(
        list(user_docs.values()),
        on_duplicate="ignore"
    )

    trusts.import_bulk(
        edge_docs,
        on_duplicate="ignore"
    )

    loaded = min(i + BATCH_SIZE, len(rows))
    print(f"Loaded {loaded}/{len(rows)}")

elapsed = time.perf_counter() - start


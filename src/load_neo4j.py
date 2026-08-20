import csv
import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

CSV_FILE = "data/processed/relationships.csv"
BATCH_SIZE = 5000

print("Connecting to Neo4j...")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

start_time = time.perf_counter()

with driver.session(database=DATABASE) as session:

    print("Connection successful!")

    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print(f"Rows found: {len(rows)}")

    START_INDEX= 0

    for i in range(START_INDEX, len(rows), BATCH_SIZE):

        batch = rows[i:i + BATCH_SIZE]

        data = [
            {
                "source": row["source"],
                "target": row["target"]
            }
            for row in batch
        ]

        session.run(
            """
            UNWIND $rows AS row

            MERGE (a:User {id: row.source})
            MERGE (b:User {id: row.target})

            MERGE (a)-[:TRUSTS]->(b)
            """,
            rows=data
        ).consume()

        loaded = min(i + BATCH_SIZE, len(rows))
        print(f"Loaded {loaded}/{len(rows)}")

elapsed = time.perf_counter() - start_time

driver.close()

print(f"Finished loading data in {elapsed:.2f} seconds.")
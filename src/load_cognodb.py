import csv
import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USER")
PASSWORD = os.getenv("COGNODB_PASSWORD")

CSV_FILE = "data/processed/relationships.csv"
BATCH_SIZE = 1000


def load_data():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    start_time = time.perf_counter()

    with driver.session() as session:

        # Load nodes first
        print("Loading nodes...")

        nodes = set()

        with open(CSV_FILE, newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                nodes.add(int(row["source"]))
                nodes.add(int(row["target"]))

        node_list = list(nodes)

        for i in range(0, len(node_list), BATCH_SIZE):
            batch = node_list[i:i + BATCH_SIZE]

            session.run(
                """
                UNWIND $ids AS id
                MERGE (:User {id: id})
                """,
                ids=batch
            ).consume()

        print(f"Loaded {len(node_list)} nodes")

        # Load relationships
        print("Loading relationships...")

        batch = []
        loaded = 0

        with open(CSV_FILE, newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                batch.append({
                    "source": int(row["source"]),
                    "target": int(row["target"])
                })

                if len(batch) == BATCH_SIZE:
                    session.run(
                        """
                        UNWIND $rows AS row
                        MATCH (a:User {id: row.source})
                        MATCH (b:User {id: row.target})
                        MERGE (a)-[:TRUSTS]->(b)
                        """,
                        rows=batch
                    ).consume()

                    loaded += len(batch)
                    print(f"Relationships: {loaded}/100000")

                    batch.clear()

            if batch:
                session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (a:User {id: row.source})
                    MATCH (b:User {id: row.target})
                    MERGE (a)-[:TRUSTS]->(b)
                    """,
                    rows=batch
                ).consume()

                loaded += len(batch)
                print(f"Relationships: {loaded}/100000")

    elapsed = time.perf_counter() - start_time

    print()
    print("========== LOAD COMPLETE ==========")
    print(f"Nodes: {len(node_list)}")
    print(f"Relationships: {loaded}")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Relationships/second: {loaded / elapsed:.2f}")

    driver.close()


if __name__ == "__main__":
    load_data()
    

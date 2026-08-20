import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USER")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

with driver.session() as session:
    print("Clearing existing graph...")
    session.run("MATCH (n) DETACH DELETE n").consume()

    print("Creating index...")
    session.run(
        "CREATE INDEX user_id_index IF NOT EXISTS "
        "FOR (u:User) ON (u.id)"
    ).consume()

print("CognoDB is clean and ready.")

driver.close()
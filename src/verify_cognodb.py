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

    node_result = session.run(
        "MATCH (n:User) RETURN count(n) AS count"
    ).single()

    relationship_result = session.run(
        "MATCH ()-[r:TRUSTS]->() RETURN count(r) AS count"
    ).single()

    print("Nodes in CognoDB:", node_result["count"])
    print("Relationships in CognoDB:", relationship_result["count"])

driver.close()
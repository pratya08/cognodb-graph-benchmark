import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

print("Connecting to Neo4j...")
print("URI:", URI)
print("USERNAME:", USERNAME)
print("DATABASE:", DATABASE)
print("PASSWORD LOADED:", bool(PASSWORD))

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

with driver.session(database=DATABASE) as session:
    result = session.run("RETURN 1 AS test")
    print(result.single()["test"])

driver.close()

print("Connection successful!")
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USER")
password = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

driver.verify_connectivity()

print("Successfully connected to CognoDB!")

driver.close()
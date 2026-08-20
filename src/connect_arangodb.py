import os
from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()

ARANGO_HOST = os.getenv("ARANGO_HOST")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")

print("HOST:", ARANGO_HOST)
print("USERNAME:", ARANGO_USERNAME)
print("PASSWORD LOADED:", bool(ARANGO_PASSWORD))

client = ArangoClient(hosts=ARANGO_HOST)

db = client.db(
    "_system",
    username=ARANGO_USERNAME,
    password=ARANGO_PASSWORD
)

print("Connection successful!")

print("Server version:", db.version())
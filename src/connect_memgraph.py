import os
from dotenv import load_dotenv
from gqlalchemy import Memgraph

load_dotenv()

HOST = os.getenv("MEMGRAPH_HOST")
PORT = int(os.getenv("MEMGRAPH_PORT", 7687))
USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")

print("HOST:", HOST)
print("PORT:", PORT)
print("USERNAME:", USERNAME)
print("PASSWORD LOADED:", bool(PASSWORD))

memgraph = Memgraph(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    encrypted=True
)

result = memgraph.execute_and_fetch(
    "RETURN 1 AS test"
)

print("Connection successful!")
print(list(result))
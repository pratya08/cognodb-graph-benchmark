import os
import random
from arango import ArangoClient
from dotenv import load_dotenv

from benchmark_utils import benchmark_query, save_result

load_dotenv()


def main():
    print("Connecting to ArangoDB...")

    uri = os.getenv("ARANGO_HOST")
    username = os.getenv("ARANGO_USERNAME")
    password = os.getenv("ARANGO_PASSWORD")
    database = os.getenv("ARANGO_DATABASE", "_system")

    client = ArangoClient(hosts=uri)
    db = client.db(
        database,
        username=username,
        password=password
    )

    print("Connection successful!")

    # Get available user IDs
    cursor = db.aql.execute(
        """
        FOR u IN users
            RETURN u._key
        """
    )

    start_nodes = list(cursor)

    if not start_nodes:
        raise RuntimeError("No users found in ArangoDB.")

    print(f"Starting users available: {len(start_nodes)}")

    # --------------------------------------------------
    # POINT LOOKUP
    # --------------------------------------------------
    def point_lookup():
        user_id = random.choice(start_nodes)

        cursor = db.aql.execute(
            """
            RETURN DOCUMENT("users", @user_id)
            """,
            bind_vars={
                "user_id": user_id
            }
        )

        return list(cursor)

    print()
    print("=" * 50)
    print("Database : ArangoDB")
    print("Workload : point lookup")
    print("=" * 50)

    #result = benchmark_query(point_lookup)
    result = benchmark_query(point_lookup)

    save_result(
    "ArangoDB",
    "point lookup",
    result,
    "results/raw/arangodb_point_lookup.json"
    )

#print("ArangoDB point lookup benchmark complete.")

    print("ArangoDB point lookup benchmark complete.")

    # --------------------------------------------------
    # INDEXED / FILTERED LOOKUP
    # --------------------------------------------------
    def filtered_lookup():
        user_id = random.choice(start_nodes)

        cursor = db.aql.execute(
            """
            FOR u IN users
                FILTER u._key == @user_id
                RETURN u._key
            """,
            bind_vars={
                "user_id": user_id
            }
        )

        return list(cursor)

    print()
    print("=" * 50)
    print("Database : ArangoDB")
    print("Workload : indexed filtered lookup")
    print("=" * 50)

    result = benchmark_query(filtered_lookup)
    result = benchmark_query(filtered_lookup)

    save_result(
    "ArangoDB",
    "indexed filtered lookup",
    result,
    "results/raw/arangodb_indexed_filtered_lookup.json"
    )

#print("ArangoDB indexed/filtered lookup benchmark complete.")
    #print(result)

    print("ArangoDB indexed/filtered lookup benchmark complete.")


if __name__ == "__main__":
    main()

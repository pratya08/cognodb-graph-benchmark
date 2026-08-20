import os

from arango import ArangoClient
from dotenv import load_dotenv

from benchmark_utils import benchmark_query

load_dotenv()


def main():
    print("Connecting to ArangoDB...")

    uri = os.getenv("ARANGO_HOST")
    username = os.getenv("ARANGO_USERNAME", "root")
    password = os.getenv("ARANGO_PASSWORD")
    database = os.getenv("ARANGO_DATABASE", "_system")

    client = ArangoClient(hosts=uri)

    db = client.db(
        database,
        username=username,
        password=password
    )

    print("Connection successful!")

    def aggregation_query():
        cursor = db.aql.execute("""
            FOR t IN trusts
                COLLECT WITH COUNT INTO relationship_count
                RETURN relationship_count
        """)

        return list(cursor)

    print()
    print("Running ArangoDB aggregation benchmark...")
    print("Warm-up: 10 runs")
    print("Measured: 100 runs")

    result = benchmark_query(aggregation_query)

    from benchmark_utils import save_result

    save_result(
        database="ArangoDB",
        workload="aggregation",
        result=result
    )

    print()
    print("ArangoDB aggregation benchmark complete.")


if __name__ == "__main__":
    main()

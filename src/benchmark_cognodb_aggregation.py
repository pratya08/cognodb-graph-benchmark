import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

from benchmark_utils import benchmark_query, save_result

load_dotenv()


def main():
    print("Connecting to CognoDB...")

    uri = os.getenv("COGNODB_URI")
    username = os.getenv("COGNODB_USER")
    password = os.getenv("COGNODB_PASSWORD")

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    print("Connection successful!")

    def aggregation_query():
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)-[:TRUSTS]->(v:User)
                RETURN count(*) AS relationship_count
                """
            )
            result.consume()

    print()
    print("Running CognoDB aggregation benchmark...")
    print("Warm-up: 10 runs")
    print("Measured: 100 runs")

    result = benchmark_query(aggregation_query)

    save_result(
        database="CognoDB",
        workload="aggregation",
        result=result
    )

    driver.close()

    print()
    print("CognoDB aggregation benchmark complete.")


if __name__ == "__main__":
    main()

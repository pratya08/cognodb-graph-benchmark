from benchmark_utils import save_result
import os
import random

from dotenv import load_dotenv
from neo4j import GraphDatabase

from benchmark_utils import benchmark_query

load_dotenv()


def main():
    print("Connecting to Neo4j...")

    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    driver.verify_connectivity()

    print("Connection successful!")

    with driver.session(database=database) as session:
        result = session.run(
            """
            MATCH (u:User)
            RETURN u.id AS id
            LIMIT 1000
            """
        )

        start_nodes = [record["id"] for record in result]

    if not start_nodes:
        raise RuntimeError("No User nodes found in Neo4j.")

    def query():
        user_id = random.choice(start_nodes)

        with driver.session(database=database) as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[:TRUSTS]->(:User)-[:TRUSTS]->(v:User)
                RETURN v.id AS id
                """,
                user_id=user_id
            )

            return list(result)

    print()
    print("==============================================")
    print("Database : Neo4j")
    print("Workload : 2-hop traversal")
    print("==============================================")

    #benchmark_query(query)
    result = benchmark_query(query)

    print(f"Runs  : {result['runs']}")
    print(f"P50   : {result['p50_ms']:.3f} ms")
    print(f"P95   : {result['p95_ms']:.3f} ms")
    print(f"Min   : {result['min_ms']:.3f} ms")
    print(f"Max   : {result['max_ms']:.3f} ms")
    print(f"Mean  : {result['mean_ms']:.3f} ms")

    save_result(
        "Neo4j",
        "2-hop traversal",
        result,
        "results/neo4j_2hop.json"
    )

    driver.close()

    print()
    print("Neo4j 2-hop benchmark complete.")


if __name__ == "__main__":
    main()

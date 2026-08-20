import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()

BENCHMARKS = [
    # ArangoDB
    "src/benchmark_arangodb.py",
    "src/benchmark_arangodb_2hop.py",
    "src/benchmark_arangodb_3hop.py",
    "src/benchmark_arangodb_aggregation.py",
    "src/benchmark_arangodb_lookup.py",
    "src/benchmark_arangodb_mixed.py",

    # CognoDB
    "src/benchmark_cognodb.py",
    "src/benchmark_cognodb_2_3hop.py",
    "src/benchmark_cognodb_aggregation.py",
    "src/benchmark_cognodb_lookup.py",
    "src/benchmark_cognodb_mixed.py",

    # Dgraph
    "src/benchmark_dgraph.py",
    "src/benchmark_dgraph_aggregation.py",
    "src/benchmark_dgraph_lookup.py",
    "src/benchmark_dgraph_mixed.py",

    # Memgraph
    "src/benchmark_memgraph.py",
    "src/benchmark_memgraph_2hop.py",
    "src/benchmark_memgraph_3hop.py",
    "src/benchmark_memgraph_aggregation.py",
    "src/benchmark_memgraph_lookup.py",
    "src/benchmark_memgraph_mixed.py",

    # Neo4j
    "src/benchmark_neo4j.py",
    "src/benchmark_neo4j_2hop.py",
    "src/benchmark_neo4j_3hop.py",
    "src/benchmark_neo4j_aggregation.py",
    "src/benchmark_neo4j_lookup.py",
    "src/benchmark_neo4j_mixed.py",
]


def main():
    print("=" * 70)
    print("GRAPH DATABASE BENCHMARK")
    print("=" * 70)
    print(f"Running {len(BENCHMARKS)} benchmark scripts.")
    print()

    for script in BENCHMARKS:
        print("=" * 70)
        print(f"Running: {script}")
        print("=" * 70)

        result = subprocess.run(
            [sys.executable, script],
            check=False,
        )

        if result.returncode != 0:
            print()
            print(f"FAILED: {script}")
            print(f"Exit code: {result.returncode}")
            sys.exit(result.returncode)

        print(f"Completed: {script}")
        print()

    print("=" * 70)
    print("ALL BENCHMARKS COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()

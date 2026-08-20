import os
from dotenv import load_dotenv
load_dotenv()

import csv
import time
import pydgraph


CSV_FILE = "data/processed/relationships.csv"
BATCH_SIZE = 1000


def escape_string(value):
    """Escape a value for use inside a Dgraph string literal."""
    return (
        value.replace("\\", "\\\\")
             .replace('"', '\\"')
             .replace("\n", "\\n")
             .replace("\r", "\\r")
    )


def load_data():

    print("Connecting to Dgraph...")

    stub = pydgraph.DgraphClientStub(os.getenv("DGRAPH_HOST", "localhost:9080"))
    client = pydgraph.DgraphClient(stub)

    print("Connection successful!")

    # ---------------------------------------------------------
    # Read CSV
    # ---------------------------------------------------------

    print("Reading CSV...")

    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print(f"Rows found: {len(rows)}")

    if not rows:
        print("No rows found.")
        stub.close()
        return

    # ---------------------------------------------------------
    # Start timer
    # ---------------------------------------------------------

    start_time = time.perf_counter()

    # ---------------------------------------------------------
    # Process in batches
    # ---------------------------------------------------------

    for i in range(0, len(rows), BATCH_SIZE):

        batch = rows[i:i + BATCH_SIZE]

        # -----------------------------------------------------
        # Get unique users in this batch
        # -----------------------------------------------------

        users = set()

        for row in batch:
            users.add(row["source"])
            users.add(row["target"])

        users = list(users)

        # -----------------------------------------------------
        # Create a Dgraph query variable for every user
        # -----------------------------------------------------

        user_vars = {}

        query_lines = ["{"]

        for index, user_id in enumerate(users):

            variable = f"u{index}"
            user_vars[user_id] = variable

            safe_id = escape_string(user_id)

            query_lines.append(
                f'  {variable} as var(func: eq(id, "{safe_id}"))'
            )

        query_lines.append("}")

        query = "\n".join(query_lines)

        # -----------------------------------------------------
        # Create users + relationships
        # -----------------------------------------------------

        nquads = []

        # Ensure every user has an id predicate.
        #
        # uid(uX) refers to the UID found by the upsert query.
        # If the user does not exist, Dgraph can create the node.
        # -----------------------------------------------------

        for user_id in users:

            variable = user_vars[user_id]
            safe_id = escape_string(user_id)

            nquads.append(
                f'uid({variable}) <id> "{safe_id}" .'
            )

        # -----------------------------------------------------
        # Create TRUSTS relationships
        # -----------------------------------------------------

        for row in batch:

            source = row["source"]
            target = row["target"]

            source_var = user_vars[source]
            target_var = user_vars[target]

            nquads.append(
                f"uid({source_var}) <TRUSTS> uid({target_var}) ."
            )

        # -----------------------------------------------------
        # Execute upsert transaction
        # -----------------------------------------------------

        txn = client.txn()

        try:

            mutation = txn.create_mutation(
                set_nquads="\n".join(nquads)
            )

            request = txn.create_request(
                query=query,
                mutations=[mutation],
                commit_now=True
            )

            txn.do_request(request)

        except Exception as e:

            print()
            print("ERROR while loading batch:")
            print(f"Batch start: {i}")
            print(f"Batch size: {len(batch)}")
            print(e)

            raise

        finally:
            txn.discard()

        # -----------------------------------------------------
        # Progress
        # -----------------------------------------------------

        loaded = min(i + BATCH_SIZE, len(rows))

        print(f"Loaded {loaded}/{len(rows)}")

    # ---------------------------------------------------------
    # Finish
    # ---------------------------------------------------------

    elapsed = time.perf_counter() - start_time

    print()
    print("========== LOAD COMPLETE ==========")
    print(f"Relationships processed: {len(rows)}")
    print(f"Total time: {elapsed:.2f} seconds")

    if elapsed > 0:
        print(
            f"Relationships/second: "
            f"{len(rows) / elapsed:.2f}"
        )

    print("===================================")

    stub.close()


if __name__ == "__main__":
    load_data()

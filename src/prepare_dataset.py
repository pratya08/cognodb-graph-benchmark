import gzip
import random
import csv

INPUT_FILE = "data/raw/epinions.txt.gz"
OUTPUT_FILE = "data/processed/relationships.csv"

SAMPLE_SIZE = 100_000
RANDOM_SEED = 42

# Read all actual relationships
edges = []

with gzip.open(INPUT_FILE, "rt") as file:
    for line in file:
        if line.startswith("#"):
            continue

        source, target = map(int, line.split())
        edges.append((source, target))

print(f"Total relationships in source dataset: {len(edges)}")

# Select the same random sample every time
random.seed(RANDOM_SEED)
sampled_edges = random.sample(edges, SAMPLE_SIZE)

# Save the sample
with open(OUTPUT_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["source", "target"])
    writer.writerows(sampled_edges)

print(f"Sampled relationships: {len(sampled_edges)}")
print(f"Saved to: {OUTPUT_FILE}")
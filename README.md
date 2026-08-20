# CognoDB Graph Database Cloud Benchmark

> **Wexa AI Take-Home Assignment --- Graph Database Cloud Benchmarking**

A reproducible benchmark comparing **CognoDB Cloud** with **Neo4j,
Memgraph, ArangoDB, and Dgraph** across graph traversal, lookup,
aggregation, mixed concurrent read/write workloads, and data-loading
throughput.

The objective is not to manufacture a winner. It is to provide a
**repeatable, transparent, and technically defensible comparison** using
the same logical dataset, equivalent workloads, repeated measurements,
and explicit caveats.

### Executive summary

-   **5 graph databases** benchmarked.
-   **35,854 nodes/users** represented in the processed benchmark
    dataset.
-   **100,000 relationships** loaded into each database.
-   Query workloads measured with **100 warm-up + 100 measured runs**.
-   Mixed workload measured with **10 warm-up + 100 measured runs**.
-   Latency reported as **P50, P95, minimum, maximum, and mean**.
-   Data-loading time and relationship throughput recorded.
-   Environment/resource observations documented where available.
-   Secrets are loaded through environment variables rather than
    committed to the repository.
-   The final mixed workload uses **2 concurrent workers with a 50/50
    read/write split**.
-   **Mixed-workload sustained QPS was not directly measured** and is
    explicitly not inferred from latency.
-   Resource parity is **not fully verifiable** because several managed
    platforms do not expose their underlying allocations; this is
    disclosed rather than estimated.

> **Important methodology note:** The Wexa assignment requires
> equivalent vCPU/RAM/storage resources across platforms. The available
> deployment evidence does not establish full resource parity for every
> database. This README therefore distinguishes **observed allocation**,
> **observed utilization**, and **not observable** values instead of
> pretending the environments were identical.

------------------------------------------------------------------------

## Benchmark at a glance

  ---------------------------------------------------------------------
  Area                               Current status
  ---------------------------------- ----------------------------------
  Databases                          CognoDB, Neo4j, Memgraph,
                                     ArangoDB, Dgraph

  Dataset                            Epinions-derived relationship
                                     graph

  Nodes/users                        35,854

  Relationships                      100,000

  Query warm-up                      100 runs

  Query measured runs                100 runs

  Mixed warm-up                      10 runs

  Mixed measured runs                100 runs

  Mixed concurrency                  2 workers

  Mixed read/write mix               1 read + 1 write per iteration
                                     (50/50)

  Query statistics                   P50, P95, min, max, mean

  Data-loading metrics               Total wall-clock time +
                                     relationships/sec

  Sustained mixed QPS                **Not measured**

  Resource allocation                Documented where observable;
                                     otherwise **Not observable**
  ---------------------------------------------------------------------

## 1. Objective

This project benchmarks CognoDB Cloud against four other graph databases
using the same logical workloads and a common benchmark harness.

The goal is an honest and reproducible comparison rather than assuming
that any particular database will win.

The benchmark uses:

-   A common logical dataset
-   Equivalent logical workloads
-   Warm-up runs
-   Repeated measurements
-   P50/P95/min/max/mean latency statistics
-   Database-specific benchmark scripts
-   Environment-based configuration
-   Pinned Python dependencies
-   Raw result preservation
-   Explicit methodology and caveats

------------------------------------------------------------------------

## 2. Databases

  Database    Tested
  ---------- --------
  CognoDB      Yes
  Neo4j        Yes
  Memgraph     Yes
  ArangoDB     Yes
  Dgraph       Yes

------------------------------------------------------------------------

## 3. Query Benchmark Results

All latency values are in milliseconds (ms). Standard query workloads
use **100 measured runs after 100 warm-up runs**. The mixed workload has
its own 10-run warm-up configuration, documented separately below.

  ---------------------------------------------------------------------------------------------------
  Database   Workload                     P50           P95           Min           Max          Mean
  ---------- ------------------ ------------- ------------- ------------- ------------- -------------
  CognoDB    1-hop traversal          207.996       208.964       207.118       212.382       208.085

  CognoDB    2-hop traversal          197.384       198.125       196.704       204.053       197.529

  CognoDB    3-hop traversal          204.648       209.718       202.670       215.998       205.504

  CognoDB    Point lookup             212.468       213.292       211.997       214.913       212.534

  CognoDB    Indexed/filtered         212.585       213.303       211.784       213.800       212.619
             lookup                                                                     

  CognoDB    Aggregation -            501.011       568.037       440.812       649.891       508.000
             Result 1                                                                   

  CognoDB    Aggregation -            502.470       579.016       432.728       614.903       504.926
             Result 2                                                                   

  CognoDB    Mixed concurrent     **223.391**   **225.412**   **221.299**   **230.014**   **223.474**
             read/write                                                                 

  Neo4j      1-hop traversal           72.961        77.372        71.718        86.238        73.818

  Neo4j      2-hop traversal           75.222       151.459        70.725       175.494        82.341

  Neo4j      3-hop traversal          279.813     1,981.405        67.663     3,676.713       568.158

  Neo4j      Point lookup              68.242        73.841        67.106        80.861        69.146

  Neo4j      Indexed/filtered          67.664        72.354        66.753       136.988        68.884
             lookup                                                                     

  Neo4j      Aggregation               85.488        95.227        82.574       123.326        87.580

  Neo4j      Mixed concurrent          73.960        82.749        72.058       142.676        76.111
             read/write                                                                 

  Memgraph   1-hop traversal          300.199       307.734       299.161       339.630       301.558

  Memgraph   2-hop traversal          274.668       294.661       273.500       341.457       278.246

  Memgraph   3-hop traversal          274.951       293.343       273.331       373.054       277.958

  Memgraph   Point lookup             274.366       284.175       273.907       320.753       276.105

  Memgraph   Indexed/filtered         274.496       276.627       273.917       279.429       274.888
             lookup                                                                     

  Memgraph   Aggregation              294.666       299.820       293.010       310.444       295.510

  Memgraph   Mixed concurrent         547.773       561.390       546.190       615.516       550.999
             read/write                                                                 

  ArangoDB   1-hop traversal          220.435       300.841       219.457       301.913       240.986

  ArangoDB   2-hop traversal          224.731       294.744       223.880       311.403       232.399

  ArangoDB   3-hop traversal          232.480     1,166.831       221.016     5,453.243       516.246

  ArangoDB   Point lookup             241.253       277.527       240.845       312.197       245.849

  ArangoDB   Indexed/filtered         241.623       299.491       241.112       314.875       247.656
             lookup                                                                     

  ArangoDB   Aggregation              296.815       506.558       242.877       713.390       338.035

  ArangoDB   Mixed concurrent         237.009       300.496       235.981       319.769       247.095
             read/write                                                                 

  Dgraph     1-hop traversal            1.872         3.814         1.136         5.162         2.073

  Dgraph     2-hop traversal            1.499         2.192         1.262         4.299         1.597

  Dgraph     3-hop traversal            6.216        11.166         5.093        14.288         7.291

  Dgraph     Point lookup               1.243         1.520         1.067         1.948         1.265

  Dgraph     Indexed/filtered           1.257         1.673         1.084         2.695         1.306
             lookup                                                                     

  Dgraph     Aggregation              248.589       340.601       116.768       496.018       235.930

  Dgraph     Mixed concurrent           5.366         9.397         4.438        20.946         6.176
             read/write                                                                 
  ---------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Data-Loading Benchmark

Data loading has been implemented and executed for all five benchmark
databases.

The common processed dataset contains **35,854 nodes/users and 100,000
relationships**.

  ----------------------------------------------------------------------
  Database           Relationships   Total Load Time   Relationships/sec
                            Loaded               (s) 
  -------------- ----------------- ----------------- -------------------
  CognoDB                  100,000             36.34            2,752.01

  Neo4j                    100,000            866.43              115.42

  Memgraph                 100,000             53.63            1,864.63

  ArangoDB                 100,000             33.86          2,953.93\*

  Dgraph                   100,000             19.91            5,023.44
  ----------------------------------------------------------------------

\* ArangoDB throughput is calculated as `100,000 / 33.86` from the
recorded load time.

Dgraph's loader directly reported **5,023.44 relationships/sec**.

### Loading implementation

Database-specific loaders are located under:

``` text
src/load_*.py
```

The loaders read:

``` text
data/processed/relationships.csv
```

and use batching where supported. Each loader records elapsed loading
time.

The loading results are observed results for the implemented loading
procedure, not universal bulk-import benchmarks. Batching strategy,
transaction behavior, network conditions, configuration, and use of
optimized native import tooling can affect the result.

------------------------------------------------------------------------

## 5. Dataset

  Metric              Value
  --------------- ---------
  Nodes/users        35,854
  Relationships     100,000

Processed relationship data:

``` text
data/processed/relationships.csv
```

Raw data:

``` text
data/raw/
```

### Dataset source and preprocessing

The raw source file used by the benchmark is:

``` text
data/raw/epinions.txt.gz
```

The repository includes `src/prepare_dataset.py`, which prepares the
benchmark dataset from this raw Epinions relationship file.

The preprocessing pipeline:

1.  Reads the compressed `epinions.txt.gz` relationship file.
2.  Skips comment lines beginning with `#`.
3.  Extracts each relationship as a source -\> target pair.
4.  Uses a fixed random seed of `42` for reproducibility.
5.  Samples exactly 100,000 relationships from the available
    relationships.
6.  Writes the resulting common benchmark dataset to:

``` text
data/processed/relationships.csv
```

The same processed relationship dataset is used by the loaders for
CognoDB, Neo4j, Memgraph, ArangoDB, and Dgraph.

The dataset preparation configuration is explicitly defined in
`src/prepare_dataset.py`:

``` python
INPUT_FILE = "data/raw/epinions.txt.gz"
OUTPUT_FILE = "data/processed/relationships.csv"
SAMPLE_SIZE = 100_000
RANDOM_SEED = 42
```

> **Provenance note:** The repository identifies the checked-in raw file
> as `epinions.txt.gz` and documents the transformation into the
> benchmark dataset. Public Epinions datasets are available from sources
> such as Stanford SNAP, but the repository does **not** establish that
> its exact `epinions.txt.gz` file is byte-for-byte the same
> distribution as a particular public Epinions release. The exact source
> URL should therefore be verified before claiming a precise upstream
> file match. This is intentionally disclosed rather than guessed.

------------------------------------------------------------------------

## 6. Methodology

### Query repetitions

The query benchmark utility specifies:

``` text
WARMUP_RUNS = 100
BENCHMARK_RUNS = 100
```

Warm-up executions are excluded from reported query latency statistics.

Reported statistics:

-   P50
-   P95
-   Minimum
-   Maximum
-   Mean

### Traversals

The benchmark includes:

-   1-hop traversal
-   2-hop traversal
-   3-hop traversal

### Point lookup

Direct lookup by node/document identifier.

### Indexed/filtered lookup

Example ArangoDB query:

``` aql
FOR u IN users
    FILTER u._key == @user_id
    RETURN u._key
```

The exact indexed properties for every database remain to be documented.

### Aggregation

Count/group-by style workloads are used. CognoDB has two recorded
aggregation result entries; both are retained rather than silently
selecting one.

------------------------------------------------------------------------

## 7. Mixed Concurrent Read/Write Methodology

The mixed workload implementation was inspected against the benchmark
scripts and the final CognoDB result was re-run with the completed
configuration.

Each measured iteration submits:

-   **1 read operation**
-   **1 write operation**

concurrently using:

``` python
ThreadPoolExecutor(max_workers=2)
```

The benchmark waits for both futures to complete and measures the
elapsed wall-clock time for the concurrent pair using
`time.perf_counter()`.

Therefore:

> The reported mixed-workload latency represents the elapsed time of the
> concurrent read/write pair, not separate read latency and write
> latency.

### Mixed workload configuration

  Setting                                             Value
  --------------------------------- -----------------------
  Concurrent workers                                      2
  Operations per iteration                                2
  Reads per iteration                                     1
  Writes per iteration                                    1
  Read/write mix                                  50% / 50%
  Warm-up runs                                           10
  Measured runs                                         100
  Timing function                     `time.perf_counter()`
  Sustained QPS directly measured                    **No**

The mixed workload is therefore a **2-operation concurrent iteration**,
not a sustained QPS test.

### Mixed workload results

  ---------------------------------------------------------------------------
  Database          P50 (ms)    P95 (ms)    Min (ms)     Max (ms)   Mean (ms)
  -------------- ----------- ----------- ----------- ------------ -----------
  **Dgraph**       **5.366**   **9.397**   **4.438**   **20.946**   **6.176**

  **Neo4j**           73.960      82.749      72.058      142.676      76.111

  **CognoDB**        223.391     225.412     221.299      230.014     223.474

  **ArangoDB**       237.009     300.496     235.981      319.769     247.095

  **Memgraph**       547.773     561.390     546.190      615.516     550.999
  ---------------------------------------------------------------------------

> **Important:** CognoDB's final mixed-workload result above is the
> completed 10-warm-up / 100-measured run and supersedes the earlier
> provisional CognoDB mixed result in the initial draft.

### QPS / throughput

**QPS was not directly measured.**

The scripts measure elapsed latency for each concurrent read/write
iteration and do not implement a sustained request-rate or throughput
test. QPS should therefore **not be inferred from the latency values and
reported as a measured metric**.

------------------------------------------------------------------------

## Re-running the benchmark

The repository is organized so that the benchmark can be reproduced from
the code and environment configuration without placing credentials in
source control.

### 1. Install dependencies

``` bash
python -m pip install -r requirements.txt
python -m pip check
```

### 2. Configure credentials through environment variables

Create a local `.env` file or export the required variables in the
shell. Do **not** commit credentials.

Example:

``` bash
export COGNODB_URI="..."
export COGNODB_PASSWORD="..."
```

Additional database-specific variables are consumed by the corresponding
connection/benchmark scripts. `DGRAPH_HOST` is configurable for the
Dgraph deployment.

### 3. Verify Python syntax

``` bash
python -m compileall -q src
```

### 4. Run the central benchmark harness

``` bash
python run_benchmark.py
```

The central runner invokes the individual benchmark scripts with the
current Python interpreter and checks subprocess return codes.

> **Reproduction caveat:** Re-running against managed free-tier services
> can produce different timings because of network conditions,
> service-side throttling, deployment state, and resource variability.
> Reproduction means the same workload and measurement procedure can be
> executed; it does not guarantee identical millisecond values.

## 8. Reproducibility

Completed reproducibility work includes:

-   Pinned dependencies in `requirements.txt`
-   Environment-variable based database configuration
-   `.env` excluded through `.gitignore`
-   Configurable `DGRAPH_HOST`
-   Central `run_benchmark.py`
-   Python syntax verification
-   Dependency verification
-   Organized raw results

Dependency verification:

``` bash
python -m pip install -r requirements.txt
python -m pip check
```

Syntax verification:

``` bash
python -m compileall -q src
```

The central runner invokes individual benchmark scripts using the
current Python interpreter and checks subprocess return codes.

### Raw results

Raw benchmark outputs are stored under:

``` text
results/raw/
```

Mixed-workload result files include:

``` text
results/raw/cognodb_mixed.json
results/raw/neo4j_mixed.json
results/raw/memgraph_mixed.json
results/raw/arangodb_mixed.json
results/raw/dgraph_mixed.json
```

------------------------------------------------------------------------

## Fairness and comparability

The assignment explicitly requires the same or as-close-as-possible
vCPU, RAM, and storage allocation across databases. The benchmark
attempts to follow that principle, but the captured deployment evidence
does not provide equivalent hardware visibility for all platforms.

### What is directly known

-   CognoDB: captured deployment details expose 0.5 burst vCPU, 512 MB
    RAM, and 1 GiB storage.
-   Memgraph: captured deployment details expose 2 CPU and 2 GB RAM.
-   Neo4j AuraDB Free: underlying CPU/RAM/storage allocation was not
    exposed.
-   ArangoDB managed deployment: utilization percentages were visible,
    but underlying allocation was not exposed.
-   Dgraph standalone Docker: no explicit CPU or memory limits were
    configured.

### Consequence

This is **not a claim of strict hardware parity**. The results should be
read as observations of the tested deployments. Where allocation was
unavailable, the README uses **Not observable** rather than estimating
capacity from utilization or container size.

The Wexa assignment itself describes the CognoDB free tier as 0.5 vCPU,
256 MB RAM, and 1 GB disk. The captured benchmark deployment showed
**512 MB RAM and 1 GiB storage**, so the observed environment is
reported exactly rather than silently replacing it with the assignment's
generic tier description.

## 9. Environment and Instance Specifications

### Client environment

The benchmark client environment was a GitHub Codespaces Linux
environment.

  Item             Observed value
  ---------------- ---------------------------------
  Client machine   GitHub Codespaces
  CPU              2 vCPUs
  CPU model        AMD EPYC 7763 64-Core Processor
  RAM              7.8 GiB
  OS               Ubuntu 22.04
  Architecture     x86_64
  Python           3.12.1
  Kernel           6.8.0-1052-azure
  Virtualization   AMD-V
  Hypervisor       Microsoft
  Region           Not observable
  Network path     Not separately measured

### Database environments

  -----------------------------------------------------------------------------------
  Database   vCPU         RAM          Storage         Tier / Deployment
  ---------- ------------ ------------ --------------- ------------------------------
  CognoDB    0.5 vCPU     512 MB       1 GiB           Free / Standalone
             burst                                     

  Neo4j      Not          Not          Not observable  AuraDB Free
             observable   observable                   

  Memgraph   2 CPU        2 GB         14 GB           Free deployment
                                       used/observed   

  ArangoDB   Allocation   Allocation   Allocation not  Managed deployment
             not          not          observable      
             observable   observable                   

  Dgraph     Not          Not          Not observable  Self-hosted Docker
             observable   observable                   (`dgraph/standalone:latest`)

** NOT OBSERVABLE IN THE SENSE THAT THE FREE IS NOT SHOWING THE METRICS
  -----------------------------------------------------------------------------------

### CognoDB observed environment details

The captured CognoDB deployment information showed:

-   Region: `us-east4` / N. Virginia
-   Version: `v0.9.11`
-   512 MB RAM
-   Burst to 0.5 vCPU
-   1 GiB storage
-   Approximately 181 MB disk used
-   Approximately 38.7 MB RSS / 8%
-   CPU observed at 0% at the captured point
-   Approximately 98.9% cache hit ratio
-   Maximum 200 connections
-   Up to 500 IOPS
-   Maximum 50,000 result rows
-   Estimated cost shown as \$0

These values are deployment/observation data from the captured
environment and should not be interpreted as universal CognoDB resource
requirements.

### Memgraph observed environment details

The captured Memgraph deployment information showed:

-   Version: `v3.12.0`
-   Region: Europe (Frankfurt)
-   2 CPU
-   2 GB RAM
-   Approximately 2 GB RAM used at the captured point
-   Approximately 14 GB disk used
-   Approximately 0.05 GB network used
-   Running deployment

### Neo4j observed environment details

The captured Neo4j deployment was:

-   AuraDB Free
-   Version: `2026.07`
-   35,854 nodes
-   100,000 relationships

The captured Free-tier information did not expose underlying vCPU, RAM,
or storage allocation. These are therefore reported as **Not
observable** rather than estimated.

### ArangoDB observed environment details

The captured ArangoDB monitoring information showed:

-   Managed deployment
-   CPU utilization: **52.54%**
-   Memory utilization: **43.14%**
-   Disk utilization: **0.85%**

These are observed utilization percentages, not underlying
vCPU/RAM/storage allocations. The benchmark does not convert these
percentages into hardware capacities.

### Dgraph resource inspection

Dgraph was run as:

``` text
dgraph/standalone:latest
```

in Docker.

Docker inspection showed:

``` text
NanoCPUs = 0
Memory = 0
Mounts = []
```

Therefore:

-   No explicit CPU limit was configured.
-   No explicit memory limit was configured.
-   No persistent Docker volume was mounted.
-   Dgraph-specific vCPU/RAM/storage allocation cannot be established
    from the deployment configuration and is reported as **Not
    observable** rather than estimated.

The observed `docker ps -a --size` output showed approximately:

-   Container size: **25.2 MB**
-   Virtual size: **230 MB**

These are Docker container/writable-layer measurements and are **not
treated as Dgraph stored-data size**.

The inspected Dgraph containers used `dgraph/standalone:latest`, exposed
ports 8080 and 9080, and the containers shown by the inspection were
exited with code 255 after the benchmark run.

------------------------------------------------------------------------

## 10. Resource and Footprint Metrics

The benchmark follows the rule that unavailable resource metrics are
marked **Not observable** rather than estimated.

  ------------------------------------------------------------------------------------
  Metric            CognoDB      Neo4j        Memgraph     ArangoDB      Dgraph
  ----------------- ------------ ------------ ------------ ------------- -------------
  vCPU              0.5 vCPU     Not          2 CPU        Not           Not
                    burst        observable                observable    observable

  RAM               512 MB       Not          2 GB         Not           Not
                                 observable                observable    observable

  Storage           1 GiB        Not          Not          Not           Not
  allocation                     observable   observable   observable    observable

  Observed disk     \~181 MB     Not          \~14 GB      0.85%         Not
  usage                          observable                utilization   observable

  Memory usage      \~38.7 MB    Not          \~2 GB       43.14%        Not
                    RSS / 8%     observable   observed     utilization   observable

  CPU observation   0% at        Not          Not          52.54%        Not
                    captured     observable   separately   utilization   observable
                    point                     recorded                   

  Tier/deployment   Free /       AuraDB Free  Free         Managed       Self-hosted
                    Standalone                deployment   deployment    Docker
  ------------------------------------------------------------------------------------

**Important:** Storage usage and resource utilization are kept separate
from resource allocation. A percentage or container size is not
converted into an inferred hardware capacity.

------------------------------------------------------------------------

## 11. Wexa Assignment Metric Coverage

The assignment asks for data loading, 1/2/3-hop traversal latency, point
and indexed/filtered lookups, aggregation, mixed concurrent read/write
throughput, and observable footprint/resource metrics.

  -----------------------------------------------------------------------
  Required metric         Status in this          Notes
                          repository              
  ----------------------- ----------------------- -----------------------
  Data loading: total     **Measured**            Recorded for all five
  wall-clock time                                 databases

  Data loading:           **Measured**            Recorded for all five
  relationships/sec                               databases

  Data loading: nodes/sec **Not recorded**        Not inferred

  1-hop latency           **Measured**            P50/P95/min/max/mean

  2-hop latency           **Measured**            P50/P95/min/max/mean

  3-hop latency           **Measured**            P50/P95/min/max/mean

  Point lookup            **Measured**            P50/P95/min/max/mean

  Indexed/filtered lookup **Measured**            P50/P95/min/max/mean

  Aggregation             **Measured**            CognoDB has two
                                                  recorded result entries

  Mixed read/write        **Measured**            2 workers, 50/50, 10
                                                  warm-ups + 100 measured

  Sustained mixed QPS     **Not measured**        No sustained
                                                  request-rate harness
                                                  was implemented

  Stored data footprint   **Partially             Reported only where
                          observable**            evidence exists

  Memory usage            **Partially             Reported only where
                          observable**            evidence exists

  vCPU/RAM/storage        **Partially             Managed platforms may
  allocation              observable**            not expose it

  Index configuration     **Not fully             Exact per-platform
                          documented**            index disclosure
                                                  remains

  Client environment      **Documented**          GitHub Codespaces
                                                  environment captured

  Caveats/fairness        **Documented**          Includes resource
                                                  visibility and
                                                  network/service
                                                  variability
  -----------------------------------------------------------------------

## 12. Results Interpretation

### How to read these results

Latency numbers are **lower-is-better**. P50 represents the median
observed latency, while P95 exposes the tail of the distribution. A
large P95-to-P50 gap indicates that some requests experienced materially
slower execution even when the median was relatively low.

Data-loading throughput is **higher-is-better**, but it is specific to
the implemented application-level loading procedure. It should not be
interpreted as a universal bulk-import ranking.

Dgraph reports the lowest latency in the current traversal and lookup
workloads, while Neo4j is also relatively low-latency compared with
CognoDB, Memgraph, and ArangoDB in these runs.

For loading, Dgraph recorded the highest observed relationship
throughput, followed by ArangoDB and CognoDB. Neo4j recorded
substantially longer loading time in the current application-level
loader.

For the final mixed concurrent read/write benchmark, Dgraph recorded the
lowest measured median and mean latency, followed by Neo4j. CognoDB's
final mean was approximately 223.5 ms, ArangoDB's approximately 247.1
ms, and Memgraph's approximately 551.0 ms.

Some workloads have substantial tail latency. For example:

-   Neo4j 3-hop traversal: P50 \~ 279.8 ms vs P95 \~ 1,981.4 ms
-   ArangoDB 3-hop traversal: P50 \~ 232.5 ms vs P95 \~ 1,166.8 ms
-   ArangoDB 3-hop maximum: \~ 5,453.2 ms

CognoDB's current query results show relatively stable latency for
1-hop, 2-hop, point lookup, and indexed/filtered lookup, while its
aggregation workloads are substantially slower than its traversal
workloads.

These are benchmark-specific observations and should not be presented as
universal database rankings.

------------------------------------------------------------------------

## 13. Caveats

The benchmark results represent the observed performance of the tested
database deployments under the documented workload and measurement
procedure. They should be interpreted as benchmark-specific observations
rather than universal rankings of the databases.

-   **Cloud and network variability:** Managed database services can
    experience variation due to network latency, shared infrastructure,
    service load, caching, and deployment state.
-   **Resource visibility:** Database platforms expose infrastructure
    resources differently. Resource values are reported only where they
    are directly observable from the deployment or platform
    configuration.
-   **Query implementation:** The workloads are logically equivalent
    across databases, while the actual queries use each database's
    native query language and client library.
-   **Indexing and configuration:** Query performance can be influenced
    by indexing, caching, transaction behavior, query planning, and
    database-specific configuration.
-   **Data loading:** Loading throughput reflects the loading procedures
    implemented in this repository, including their batching and
    transaction behavior. It is not intended to represent every
    database's optimized native bulk-import capability.
-   **Latency statistics:** P50 and P95 describe the observed latency
    distribution for the measured runs. Tail latency can be affected by
    transient infrastructure and service conditions.
-   **Mixed workload:** The mixed workload measures concurrent
    read/write execution using the documented client-side concurrency
    model. Its latency statistics should be interpreted together with
    the workload definition rather than as a standalone throughput
    ranking.
-   **Dataset:** The benchmark uses the documented Epinions-derived
    relationship dataset and the fixed preprocessing procedure described
    in this README.
-   **Metric interpretation:** Metrics are reported using the units and
    measurement procedures defined by the benchmark. Values are not
    extrapolated beyond the observations collected during the runs.

> **Benchmark principle:** The results are presented as measured
> observations from a controlled and reproducible benchmark procedure,
> with methodological context provided so that the numbers can be
> interpreted appropriately.

## 14. Security

Do not commit:

-   Database passwords
-   API keys
-   Private connection URIs
-   Other credentials

Use environment variables, for example:

``` bash
export COGNODB_URI="..."
export COGNODB_PASSWORD="..."
```

Keep `.env` excluded through `.gitignore`.

Before pushing the repository, perform a final secret review:

``` bash
git status
git diff --cached
git grep -n -E 'password|api[_-]?key|secret|token|bolt\+s://|Authorization' -- ':!README.md'
```

Do not commit any real credential values discovered by this check.

------------------------------------------------------------------------

## 15. Project Structure

``` text
cognodb-graph-benchmark/
|-- data/
|   |-- processed/
|   `-- raw/
|-- results/
|   `-- raw/
|-- src/
|   |-- benchmark_*.py
|   |-- connect_*.py
|   |-- load_*.py
|   `-- ...
|-- run_benchmark.py
|-- README.md
`-- requirements.txt
```

------------------------------------------------------------------------

## 16. Final Takeaway

Query workloads, data-loading workloads, reproducibility checks,
resource inspection, client-environment documentation, and mixed
concurrent read/write methodology have now been implemented and
measured/documented across the five databases.

The final mixed workload uses 2 concurrent workers with a 50/50
read/write split, 10 warm-up runs, and 100 measured runs. The final
observed mean latencies were:

  Database     Mixed workload mean
  ---------- ---------------------
  Dgraph              **6.176 ms**
  Neo4j              **76.111 ms**
  CognoDB           **223.474 ms**
  ArangoDB          **247.095 ms**
  Memgraph          **550.999 ms**

The current results are observations from this benchmark setup, not
universal claims about database performance.

The remaining work is primarily final documentation/provenance, index
disclosure, optional resource measurements where observable, final
runner verification, visualization, and final repository cleanup.

------------------------------------------------------------------------

## References and provenance

-   **Wexa AI Candidate Take-Home Assignment --- Graph Database Cloud
    Benchmarking:** defines the required dataset, metrics, fairness
    rules, reproducibility expectations, README deliverables, and
    honesty/caveat requirements.
-   **Epinions public dataset references:** Stanford SNAP maintains
    public Epinions network datasets and documents their node/edge
    statistics and provenance. The exact checked-in `epinions.txt.gz`
    file used here should be matched to an upstream release before
    claiming exact file-level provenance.

------------------------------------------------------------------------

## License / benchmark note

This repository contains benchmark code and derived benchmark data for
evaluation purposes. Dataset ownership and redistribution terms remain
those of the original dataset source. The benchmark results are
observations from the stated environments and workload implementation
and are not universal performance guarantees.

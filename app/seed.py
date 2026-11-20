"""Seed rows for a fresh database.

The app is the live index for the database-labs collection. These rows mirror
the table in devarent/database-labs.
"""

OWNER = "devarent"


def repo(slug: str) -> str:
    return f"https://github.com/{OWNER}/{slug}"


SEED_ENGINES = [
    {
        "name": "Firebird",
        "category": "Relational",
        "runtime": "docker",
        "repo_url": repo("firebird-lab"),
        "notes": "Embeddable SQL server; isql and JDBC exercises.",
    },
    {
        "name": "IBM Db2",
        "category": "Relational",
        "runtime": "docker",
        "repo_url": repo("ibm-db2-lab"),
        "notes": "Db2 Community Edition with a sales schema.",
    },
    {
        "name": "MariaDB",
        "category": "Relational",
        "runtime": "docker",
        "repo_url": repo("mariadb-practicum"),
        "notes": "Procedures, triggers, indexes, backup and restore.",
    },
    {
        "name": "Microsoft SQL Server",
        "category": "Relational",
        "runtime": "docker",
        "repo_url": repo("sql-server-lab"),
        "notes": "T-SQL, execution plans, and transactions.",
    },
    {
        "name": "CockroachDB",
        "category": "Distributed SQL",
        "runtime": "docker",
        "repo_url": repo("cockroachdb-lab"),
        "notes": "Multi-node cluster, serializable transactions, ranges.",
    },
    {
        "name": "InterSystems IRIS",
        "category": "Multi-model",
        "runtime": "docker",
        "repo_url": repo("intersystems-iris-lab"),
        "notes": "Object, relational, and document access to one store.",
    },
    {
        "name": "Databricks SQL",
        "category": "Lakehouse",
        "runtime": "cloud",
        "repo_url": repo("databricks-sql-lab"),
        "notes": "Serverless SQL warehouse, Delta tables, time travel.",
    },
    {
        "name": "Snowflake",
        "category": "Cloud warehouse",
        "runtime": "cloud",
        "repo_url": repo("snowflake-lab"),
        "notes": "Virtual warehouses, stages, QUALIFY, zero-copy clones.",
    },
    {
        "name": "Amazon Redshift",
        "category": "Cloud warehouse",
        "runtime": "cloud",
        "repo_url": repo("redshift-lab"),
        "notes": "Distribution styles, sort keys, COPY from S3.",
    },
    {
        "name": "Teradata",
        "category": "Enterprise warehouse",
        "runtime": "cloud",
        "repo_url": repo("teradata-lab"),
        "notes": "Primary indexes, COLLECT STATISTICS, QUALIFY.",
    },
    {
        "name": "Vertica",
        "category": "Columnar analytics",
        "runtime": "cloud",
        "repo_url": repo("vertica-lab"),
        "notes": "Projections, segmentation, COPY, EXPLAIN.",
    },
    {
        "name": "Google BigQuery",
        "category": "Serverless analytics",
        "runtime": "docker",
        "repo_url": repo("bigquery-lab"),
        "notes": "Local emulator plus a real BigQuery path.",
    },
    {
        "name": "Redis",
        "category": "Key-value",
        "runtime": "docker",
        "repo_url": repo("redis-lab"),
        "notes": "Data structures, expiry, persistence, Python client.",
    },
    {
        "name": "MongoDB",
        "category": "Document",
        "runtime": "docker",
        "repo_url": repo("mongodb-practicum"),
        "notes": "Document modeling, aggregation, indexes, CRUD.",
    },
    {
        "name": "Apache Cassandra",
        "category": "Wide-column",
        "runtime": "docker",
        "repo_url": repo("cassandra-lab"),
        "notes": "Partition keys, clustering columns, CQL.",
    },
    {
        "name": "Elasticsearch",
        "category": "Search",
        "runtime": "docker",
        "repo_url": repo("elasticsearch-lab"),
        "notes": "Mappings, bulk indexing, full-text search, aggregations.",
    },
    {
        "name": "Qdrant",
        "category": "Vector",
        "runtime": "docker",
        "repo_url": repo("qdrant-lab"),
        "notes": "Collections, payloads, similarity search, REST and Python.",
    },
    {
        "name": "ChromaDB",
        "category": "Vector",
        "runtime": "docker",
        "repo_url": repo("chromadb-lab"),
        "notes": "Explicit embeddings, collections, metadata filters.",
    },
    {
        "name": "Neo4j",
        "category": "Graph",
        "runtime": "docker",
        "repo_url": repo("neo4j-lab"),
        "notes": "Cypher patterns, variable-length paths, shortest path.",
    },
    {
        "name": "Apache Kafka",
        "category": "Streaming",
        "runtime": "docker",
        "repo_url": repo("apache-kafka-lab"),
        "notes": "KRaft cluster, topics, producers, consumers.",
    },
    {
        "name": "Apache Kylin",
        "category": "OLAP",
        "runtime": "docker",
        "repo_url": repo("apache-kylin-lab"),
        "notes": "Cubes, models, pre-aggregation over Hive tables.",
    },
    {
        "name": "VictoriaMetrics",
        "category": "Time-series",
        "runtime": "docker",
        "repo_url": repo("victoriametrics-lab"),
        "notes": "Prometheus import, PromQL, vmui.",
    },
    {
        "name": "InfluxDB",
        "category": "Time-series",
        "runtime": "docker",
        "repo_url": repo("influxdb-lab"),
        "notes": "Line protocol, Flux queries, downsampling tasks.",
    },
    {
        "name": "TDengine",
        "category": "Time-series",
        "runtime": "docker",
        "repo_url": repo("tdengine-lab"),
        "notes": "Super tables, tags, IoT telemetry, REST API.",
    },
    {
        "name": "Databend",
        "category": "Cloud-native OLAP",
        "runtime": "docker",
        "repo_url": repo("databend-lab"),
        "notes": "MySQL protocol and HTTP SQL API.",
    },
    {
        "name": "JDBC",
        "category": "Connectivity",
        "runtime": "docker",
        "repo_url": repo("jdbc-lab"),
        "notes": "Java client, connection pooling, and transactions.",
    },
]

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import ssl
import certifi

load_dotenv()


class Neo4jClient:
    def __init__(self):
        self._driver = None

    def connect(self):
        """
        Establish secure connection to Neo4j Aura.
        Uses certifi CA bundle to avoid SSL verification issues.
        """
        if self._driver is not None:
            return
        try:
            # Added configuration specifically for unstable networks/AuraDB
            uri = os.getenv("NEO4J_URI", "neo4j+s://22721863.databases.neo4j.io")
            user = os.getenv("NEO4J_USERNAME", "22721863")
            password = os.getenv("NEO4J_PASSWORD", "ThS48Vbk_n7Fb1_lpVuYyQMlw7a55BPemYZwarUyiBw")

            self._driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=300,  # Refresh connection every 5 mins
                keep_alive=True,              # Send pings to keep connection open
                connection_acquisition_timeout=60 # Wait up to 60s for a connection
            )
            self._driver.verify_connectivity()
            print("✅ Connected to Neo4j Graph Database")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            self._driver = None


    @property
    def driver(self):
        if self._driver is None:
            self.connect()
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None
            print("🔌 Neo4j connection closed")

    def clear_database(self):
        """
        Deletes all nodes and relationships in the database.
        USE WITH CAUTION.
        """
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)
            print("🗑️ Neo4j Database cleared successfully")

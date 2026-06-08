from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def build_graph(self, entities: list, relationships: list):
        with self.driver.session() as session:
            for entity in entities:
                session.execute_write(self._create_entity, entity)
            for rel in relationships:
                session.execute_write(self._create_relationship, rel)

    @staticmethod
    def _create_entity(tx, entity):
        query = (
            f"MERGE (n:{entity['type']} {{name: $name}}) "
            "ON CREATE SET n.created_at = timestamp()"
        )
        tx.run(query, name=entity['name'])

    @staticmethod
    def _create_relationship(tx, rel):
        query = (
            f"MATCH (a {{name: $source}}) "
            f"MATCH (b {{name: $target}}) "
            f"MERGE (a)-[r:{rel['relation']}]->(b)"
        )
        tx.run(query, source=rel['source'], target=rel['target'])

neo4j_client = Neo4jClient()

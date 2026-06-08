from fastapi import APIRouter, Depends
from app.api import deps
from app.graph.neo4j_client import neo4j_client
from app.models.user import User

router = APIRouter()

@router.get("/entities")
def get_entities(current_user: User = Depends(deps.get_current_active_user)):
    query = "MATCH (n) RETURN labels(n)[0] AS type, n.name AS name LIMIT 100"
    with neo4j_client.driver.session() as session:
        result = session.run(query)
        return [{"type": record["type"], "name": record["name"]} for record in result]

@router.get("/relationships")
def get_relationships(current_user: User = Depends(deps.get_current_active_user)):
    query = "MATCH (a)-[r]->(b) RETURN a.name AS source, type(r) AS relation, b.name AS target LIMIT 100"
    with neo4j_client.driver.session() as session:
        result = session.run(query)
        return [{"source": record["source"], "relation": record["relation"], "target": record["target"]} for record in result]

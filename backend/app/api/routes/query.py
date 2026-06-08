from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api import deps
from app.models.user import User

from app.ai.gemini_client import embed_text, extract_entities, generate_answer
from app.vector.chroma_client import chroma_client
from app.graph.neo4j_client import neo4j_client

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    vector_context: list[str]
    graph_context: list[str]

@router.post("", response_model=QueryResponse)
def handle_query(
    request: QueryRequest
):
    query = request.query
    
    # 1. Vector Retrieval
    query_embeddings = embed_text([query])
    vector_context = []
    if query_embeddings:
        vector_results = chroma_client.query(query_embeddings[0], n_results=3)
        if vector_results:
            vector_context = vector_results

    # 2. Graph Retrieval
    try:
        entities = extract_entities(query)
    except Exception as e:
        print(f"Error extracting entities: {e}")
        entities = []
        
    graph_context = []
    
    if entities:
        with neo4j_client.driver.session() as session:
            for entity in entities:
                # Get 1-hop relationships for the extracted entities
                cypher = """
                MATCH (a)-[r]-(b)
                WHERE toLower(a.name) = toLower($name)
                   OR toLower(a.name) CONTAINS toLower($name)
                   OR toLower($name) CONTAINS (toLower(a.name) + ' ')
                   OR toLower($name) CONTAINS (' ' + toLower(a.name))
                RETURN a.name AS source, type(r) AS relation, b.name AS target
                LIMIT 10
                """
                result = session.run(cypher, name=entity['name'])
                for record in result:
                    graph_context.append(f"{record['source']} -[{record['relation']}]-> {record['target']}")
    else:
        with neo4j_client.driver.session() as session:
            cypher = """
            MATCH (n)
            RETURN n.name AS name, labels(n) AS label
            LIMIT 50
            """
            result = session.run(cypher)
            for record in result:
                graph_context.append(f"Entity: {record['name']} (Type: {record['label'][0] if record['label'] else 'Unknown'})")
    # 3. Answer Generation
    vector_text = "\n".join(vector_context)
    graph_text = "\n".join(graph_context)
    
    try:
        answer = generate_answer(query, vector_text, graph_text)
    except Exception as e:
        print(f"Error generating answer: {e}")
        if "429" in str(e):
            answer = "I'm currently experiencing high traffic and have exceeded my API rate limits. Please try again in a minute!"
        else:
            answer = f"An error occurred while connecting to the AI model: {e}"
    
    return QueryResponse(
        answer=answer,
        vector_context=vector_context,
        graph_context=graph_context
    )

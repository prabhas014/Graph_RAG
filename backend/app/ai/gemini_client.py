import json
from google import genai
from pydantic import BaseModel, Field
from typing import Literal
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

class Entity(BaseModel):
    name: str = Field(description="Name of the entity")
    type: str = Field(description="Type of the entity (Person, Organization, Location, Event, Product, Technology, Dataset, Research Paper)")

class ExtractionResult(BaseModel):
    entities: list[Entity] = Field(description="List of extracted entities")

class Relationship(BaseModel):
    source: str = Field(description="Source entity name")
    relation: Literal["IS_A", "TYPE_OF", "USES", "CONTAINS", "IMPLEMENTS", "EXTENDS", "CREATED_BY", "PART_OF", "HAS_TYPE"] = Field(description="Relationship type")
    target: str = Field(description="Target entity name")

class RelationshipResult(BaseModel):
    relationships: list[Relationship] = Field(description="List of extracted relationships")

def extract_entities(text: str) -> list[dict]:
    if not client:
        print("Warning: Gemini client not initialized. Missing API key.")
        return []
    prompt = f"Extract entities from the following text:\n\n{text}"
    response = client.models.generate_content(
        model='gemma-4-26b-a4b-it',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ExtractionResult,
        },
    )
    result = json.loads(response.text)
    return result.get("entities", [])

def extract_relationships(text: str, entities: list[dict]) -> list[dict]:
    if not client:
        return []
    entity_names = [e["name"] for e in entities]
    prompt = f"""Extract relationships between the following entities: {', '.join(entity_names)} from the text below.
Only create relationships that are explicitly stated in the document.
Do NOT create generic RELATED_TO edges.
Allowed relationships: IS_A, TYPE_OF, USES, CONTAINS, IMPLEMENTS, EXTENDS, CREATED_BY, PART_OF, HAS_TYPE.
Reject vague relationships.
Examples:
GOOD: Class -> HAS_TYPE -> R6, R Programming -> USES -> Vector
BAD: R6 -> RELATED_TO -> Ravi, Vector -> RELATED_TO -> Person

Text: {text}"""
    response = client.models.generate_content(
        model='gemma-4-26b-a4b-it',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': RelationshipResult,
        },
    )
    result = json.loads(response.text)
    return result.get("relationships", [])

def embed_text(texts: list[str]) -> list[list[float]]:
    if not client:
        print("Warning: Gemini client not initialized. Missing API key.")
        return []
        
    try:
        embeddings = []
        for text in texts:
            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )
            embeddings.append(response.embeddings[0].values)
        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

def generate_answer(query: str, vector_context: str, graph_context: str) -> str:
    if not client:
        return "Warning: Gemini client not initialized. Missing API key."
        
    prompt = f"""You are a helpful and knowledgeable Graph RAG assistant. 
Answer the user's question using the provided context.
The context contains two parts:
1. Vector Context (Text snippets from documents)
2. Graph Context (Relationships between entities found in the knowledge graph)

Synthesize the information from both contexts to provide a comprehensive, accurate, and multi-hop reasoning answer.
IMPORTANT FORMATTING RULES:
- Write your response as a single, clean paragraph.
- DO NOT use bullet points, numbered lists, or bold text.
- Write naturally like a human explaining a concept.
If the context doesn't contain the answer, say you don't have enough information.

Vector Context:
{vector_context}

Graph Context:
{graph_context}

User Question: {query}
Answer:"""

    response = client.models.generate_content(
        model='gemma-4-26b-a4b-it',
        contents=prompt
    )
    return response.text

import traceback
from app.ai.gemini_client import extract_entities, embed_text

try:
    print("Testing extraction...")
    entities = extract_entities("Larry Page and Sergey Brin founded Google.")
    print("Entities:", entities)
    print("Testing embedding...")
    emb = embed_text(["Larry Page and Sergey Brin founded Google."])
    print("Embeddings:", emb[0][:5] if emb else [])
except Exception as e:
    traceback.print_exc()

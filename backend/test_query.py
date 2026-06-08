import traceback
from app.api.routes.query import handle_query, QueryRequest

try:
    req = QueryRequest(query="test")
    res = handle_query(req)
    print("Success:", res)
except Exception as e:
    traceback.print_exc()

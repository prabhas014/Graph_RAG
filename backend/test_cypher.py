from app.graph.neo4j_client import neo4j_client

cypher = """
MATCH (a)-[r]-(b)
WHERE toLower(a.name) = toLower($name)
   OR toLower(a.name) CONTAINS toLower($name)
   OR toLower($name) CONTAINS (toLower(a.name) + ' ')
   OR toLower($name) CONTAINS (' ' + toLower(a.name))
RETURN a.name AS source, type(r) AS relation, b.name AS target
LIMIT 10
"""

with neo4j_client.driver.session() as session:
    result = session.run(cypher, name="R Programming")
    print("Results for 'R Programming':")
    for record in result:
        print(f"{record['source']} -[{record['relation']}]-> {record['target']}")
        
    result = session.run(cypher, name="R6 Class")
    print("\nResults for 'R6 Class':")
    for record in result:
        print(f"{record['source']} -[{record['relation']}]-> {record['target']}")

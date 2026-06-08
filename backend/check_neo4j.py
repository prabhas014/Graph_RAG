from app.graph.neo4j_client import neo4j_client

with neo4j_client.driver.session() as session:
    print("Checking Node count...")
    result = session.run("MATCH (n) RETURN count(n) as count")
    print("Nodes:", result.single()["count"])
    
    print("Checking Relationship count...")
    result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
    print("Relationships:", result.single()["count"])
    
    print("Sample Nodes:")
    result = session.run("MATCH (n) RETURN n.name as name, labels(n) as label LIMIT 10")
    for record in result:
        print(record["name"], record["label"])

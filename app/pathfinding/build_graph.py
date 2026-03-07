from collections import defaultdict
from app.models import Edge, Floor

def build_graph(building_id):
    # Fetch all floors for the building
    floors = Floor.query.filter_by(building_id=building_id).all()
    if not floors:
        raise ValueError("Building not found or has no floors")
    
    floor_map = {f.floor_id: f for f in floors}
    floor_ids = list(floor_map.keys())
    
    # Fetch all edges for these floors
    db_edges = Edge.query.filter(Edge.floor_id.in_(floor_ids)).all()
    
    graph = defaultdict(list)
    
    for edge in db_edges:
        u = edge.start_node_id
        v = edge.end_node_id
        
        # Apply the scale of the floor assigned to the edge
        floor = floor_map.get(edge.floor_id)
        scale = floor.scale if floor and floor.scale else 1.0
        
        weight = edge.distance * scale
        
        graph[u].append((v, weight))
        graph[v].append((u, weight))
        
    return graph
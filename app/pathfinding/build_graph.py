from collections import defaultdict
from app.models import Edge, Floor

def build_graph(floor_id):
    edges = Edge.query.filter_by(floor_id=floor_id).all()
    floor = Floor.query.get(floor_id)
    if not floor:
        raise ValueError("Floor not found")
    scale = floor.scale if floor.scale else 1.0
    
    edges = [
        {
            'from': edge.start_node_id,
            'to': edge.end_node_id,
            'weight': edge.distance * scale
        } for edge in edges
    ]
    
    graph = defaultdict(list)
    
    for edge in edges:
        u = edge['from']
        v = edge['to']
        weight = edge['weight']
        
        graph[u].append((v, weight))
        graph[v].append((u, weight))
        
    return graph
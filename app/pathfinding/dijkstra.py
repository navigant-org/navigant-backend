import heapq

def findpath(start_node, end_node, graph):
    pq = [(0, start_node)]  # priority queue of (cost, node)
    
    distances = {start_node: 0}
    previous_nodes = {start_node: None}
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_node == end_node:
            break
        
        if current_distance > distances.get(current_node, float('inf')):
            continue
        
        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight
            
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
                
    path = []
    node = end_node
    
    if end_node not in previous_nodes:
        return float('inf'), []  # No path found
    
    while node is not None:
        path.append(node)
        node = previous_nodes.get(node)
        
    path.reverse()
    
    return distances[end_node], path
"""
Graph algorithms demonstrations for the Algorithms module.
"""

import heapq
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Tuple, Set
from .base import AlgorithmDemo


class Graph:
    """Graph implementation with adjacency list representation."""
    
    def __init__(self, directed=False):
        self.graph = defaultdict(list)
        self.directed = directed
        self.vertices = set()
    
    def add_edge(self, u, v, weight=1):
        """Add edge between vertices u and v."""
        self.graph[u].append((v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
        
        if not self.directed:
            self.graph[v].append((u, weight))
    
    def get_neighbors(self, vertex):
        """Get neighbors of a vertex."""
        return self.graph[vertex]
    
    def print_graph(self):
        """Print graph representation."""
        print("Graph adjacency list:")
        for vertex in sorted(self.vertices):
            neighbors = [f"{neighbor}({weight})" for neighbor, weight in self.graph[vertex]]
            print(f"  {vertex}: {neighbors}")


class GraphAlgorithms(AlgorithmDemo):
    """Demonstration class for graph algorithms."""
    
    def __init__(self):
        super().__init__("graph_algorithms")
    
    def _setup_examples(self) -> None:
        """Setup graph algorithm examples."""
        self.examples = {
            "graph_representation": {
                "code": '''
from collections import defaultdict, deque

class Graph:
    """Graph implementation with adjacency list representation."""
    
    def __init__(self, directed=False):
        self.graph = defaultdict(list)
        self.directed = directed
        self.vertices = set()
    
    def add_edge(self, u, v, weight=1):
        """Add edge between vertices u and v."""
        self.graph[u].append((v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
        
        if not self.directed:
            self.graph[v].append((u, weight))
    
    def get_neighbors(self, vertex):
        """Get neighbors of a vertex."""
        return self.graph[vertex]
    
    def print_graph(self):
        """Print graph representation."""
        print("Graph adjacency list:")
        for vertex in sorted(self.vertices):
            neighbors = [f"{neighbor}({weight})" for neighbor, weight in self.graph[vertex]]
            print(f"  {vertex}: {neighbors}")

# Example usage
g = Graph(directed=False)
edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'E'), ('D', 'E'), ('E', 'F')]

for u, v in edges:
    g.add_edge(u, v)

g.print_graph()
''',
                "explanation": "Graph representation using adjacency lists for efficient storage and traversal",
                "time_complexity": "O(V + E) space, O(V) for neighbor lookup",
                "space_complexity": "O(V + E)"
            },
            
            "graph_traversal": {
                "code": '''
def bfs(graph, start):
    """Breadth-first search traversal."""
    visited = set()
    queue = deque([start])
    traversal_order = []
    
    print(f"BFS starting from {start}:")
    
    while queue:
        vertex = queue.popleft()
        
        if vertex not in visited:
            visited.add(vertex)
            traversal_order.append(vertex)
            print(f"  Visiting {vertex}")
            
            # Add unvisited neighbors to queue
            for neighbor, _ in graph.graph[vertex]:
                if neighbor not in visited:
                    queue.append(neighbor)
                    print(f"    Added {neighbor} to queue")
    
    return traversal_order

def dfs(graph, start, visited=None):
    """Depth-first search traversal."""
    if visited is None:
        visited = set()
        print(f"DFS starting from {start}:")
    
    visited.add(start)
    print(f"  Visiting {start}")
    
    for neighbor, _ in graph.graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    
    return list(visited)

def dfs_iterative(graph, start):
    """Iterative DFS using explicit stack."""
    visited = set()
    stack = [start]
    traversal_order = []
    
    print(f"Iterative DFS starting from {start}:")
    
    while stack:
        vertex = stack.pop()
        
        if vertex not in visited:
            visited.add(vertex)
            traversal_order.append(vertex)
            print(f"  Visiting {vertex}")
            
            # Add neighbors to stack (in reverse order for consistent traversal)
            neighbors = [neighbor for neighbor, _ in graph.graph[vertex]]
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return traversal_order

# Example usage
g = Graph()
edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'E'), ('D', 'E'), ('E', 'F')]
for u, v in edges:
    g.add_edge(u, v)

bfs_result = bfs(g, 'A')
print(f"BFS order: {bfs_result}")

dfs_result = dfs(g, 'A')
print(f"DFS order: {dfs_result}")
''',
                "explanation": "Graph traversal algorithms explore all vertices systematically",
                "time_complexity": "O(V + E) for both BFS and DFS",
                "space_complexity": "O(V) for visited set and queue/stack"
            },
            
            "shortest_path_dijkstra": {
                "code": '''
import heapq

def dijkstra(graph, start):
    """Dijkstra's algorithm for shortest paths."""
    # Initialize distances
    distances = {vertex: float('inf') for vertex in graph.vertices}
    distances[start] = 0
    previous = {vertex: None for vertex in graph.vertices}
    
    # Priority queue: (distance, vertex)
    pq = [(0, start)]
    visited = set()
    
    print(f"Dijkstra's algorithm starting from {start}")
    print(f"Initial distances: {dict(distances)}")
    
    while pq:
        current_distance, current_vertex = heapq.heappop(pq)
        
        if current_vertex in visited:
            continue
        
        visited.add(current_vertex)
        print(f"\\nVisiting {current_vertex} (distance: {current_distance})")
        
        # Check neighbors
        for neighbor, weight in graph.graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_distance + weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (new_distance, neighbor))
                    print(f"  Updated {neighbor}: distance = {new_distance}")
    
    return distances, previous

def get_shortest_path(start, end, previous):
    """Reconstruct shortest path from previous array."""
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    return path if path[0] == start else []

# Example usage
wg = Graph()
edges = [
    ('A', 'B', 4), ('A', 'C', 2),
    ('B', 'C', 1), ('B', 'D', 5),
    ('C', 'D', 8), ('C', 'E', 10),
    ('D', 'E', 2)
]

for u, v, w in edges:
    wg.add_edge(u, v, w)

distances, previous = dijkstra(wg, 'A')

print(f"\\nFinal shortest distances from A:")
for vertex, distance in distances.items():
    path = get_shortest_path('A', vertex, previous)
    print(f"  {vertex}: {distance} (path: {' → '.join(path)})")
''',
                "explanation": "Dijkstra's algorithm finds shortest paths from source to all vertices",
                "time_complexity": "O((V + E) log V) with binary heap",
                "space_complexity": "O(V)"
            },
            
            "shortest_path_floyd_warshall": {
                "code": '''
def floyd_warshall(graph):
    """Floyd-Warshall algorithm for all-pairs shortest paths."""
    vertices = list(graph.vertices)
    n = len(vertices)
    
    # Initialize distance matrix
    dist = [[float('inf')] * n for _ in range(n)]
    
    # Distance from vertex to itself is 0
    for i in range(n):
        dist[i][i] = 0
    
    # Fill in direct edges
    for u in vertices:
        for v, weight in graph.graph[u]:
            i, j = vertices.index(u), vertices.index(v)
            dist[i][j] = weight
    
    print("Floyd-Warshall Algorithm:")
    print(f"Vertices: {vertices}")
    
    # Main algorithm
    for k in range(n):
        print(f"\\nUsing vertex {vertices[k]} as intermediate:")
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    old_dist = dist[i][j]
                    dist[i][j] = dist[i][k] + dist[k][j]
                    print(f"  Updated dist[{vertices[i]}][{vertices[j]}]: {old_dist} → {dist[i][j]}")
    
    return dist, vertices

def print_distance_matrix(dist, vertices):
    """Print formatted distance matrix."""
    print(f"\\nAll-pairs shortest distances:")
    print("     ", end="")
    for v in vertices:
        print(f"{v:6}", end="")
    print()
    
    for i, u in enumerate(vertices):
        print(f"{u:3}: ", end="")
        for j, v in enumerate(vertices):
            if dist[i][j] == float('inf'):
                print("   ∞  ", end="")
            else:
                print(f"{dist[i][j]:6}", end="")
        print()

# Example usage
wg = Graph()
edges = [('A', 'B', 4), ('A', 'C', 2), ('B', 'C', 1), ('B', 'D', 5), ('C', 'D', 8)]
for u, v, w in edges:
    wg.add_edge(u, v, w)

dist_matrix, vertices = floyd_warshall(wg)
print_distance_matrix(dist_matrix, vertices)
''',
                "explanation": "Floyd-Warshall finds shortest paths between all pairs of vertices",
                "time_complexity": "O(V³)",
                "space_complexity": "O(V²)"
            },
            
            "cycle_detection": {
                "code": '''
def has_cycle_undirected(graph):
    """Detect cycle in undirected graph using DFS."""
    visited = set()
    
    def dfs_cycle_check(vertex, parent):
        """Helper for cycle detection in undirected graph."""
        visited.add(vertex)
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                if dfs_cycle_check(neighbor, vertex):
                    return True
            elif neighbor != parent:
                print(f"Cycle detected: back edge from {vertex} to {neighbor}")
                return True
        
        return False
    
    for vertex in graph.vertices:
        if vertex not in visited:
            if dfs_cycle_check(vertex, -1):
                return True
    return False

def has_cycle_directed(graph):
    """Detect cycle in directed graph using DFS with colors."""
    # 0: white (unvisited), 1: gray (visiting), 2: black (visited)
    color = {vertex: 0 for vertex in graph.vertices}
    
    def dfs_cycle_check(vertex):
        """Helper for cycle detection in directed graph."""
        if color[vertex] == 1:  # Gray vertex - back edge found
            print(f"Cycle detected: back edge to {vertex}")
            return True
        
        if color[vertex] == 2:  # Already processed
            return False
        
        color[vertex] = 1  # Mark as visiting
        
        for neighbor, _ in graph.graph[vertex]:
            if dfs_cycle_check(neighbor):
                return True
        
        color[vertex] = 2  # Mark as visited
        return False
    
    for vertex in graph.vertices:
        if color[vertex] == 0:
            if dfs_cycle_check(vertex):
                return True
    return False

def topological_sort(graph):
    """Topological sort for directed acyclic graph."""
    if not graph.directed:
        raise ValueError("Topological sort only applies to directed graphs")
    
    # Check for cycles first
    if has_cycle_directed(graph):
        raise ValueError("Graph has cycle - topological sort not possible")
    
    in_degree = {vertex: 0 for vertex in graph.vertices}
    
    # Calculate in-degrees
    for vertex in graph.vertices:
        for neighbor, _ in graph.graph[vertex]:
            in_degree[neighbor] += 1
    
    # Find vertices with no incoming edges
    queue = deque([v for v in graph.vertices if in_degree[v] == 0])
    topo_order = []
    
    print("Topological sort process:")
    
    while queue:
        vertex = queue.popleft()
        topo_order.append(vertex)
        print(f"  Process {vertex}")
        
        # Remove edges and update in-degrees
        for neighbor, _ in graph.graph[vertex]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                print(f"    Added {neighbor} to queue (in-degree became 0)")
    
    return topo_order

# Example usage
# Test cycle detection
print("=== Cycle Detection ===")
ug = Graph(directed=False)
cycle_edges = [('A', 'B'), ('B', 'C'), ('C', 'A')]
for u, v in cycle_edges:
    ug.add_edge(u, v)

print(f"Undirected graph has cycle: {has_cycle_undirected(ug)}")

# Test topological sort
dg = Graph(directed=True)
dag_edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')]
for u, v in dag_edges:
    dg.add_edge(u, v)

topo_result = topological_sort(dg)
print(f"Topological order: {topo_result}")
''',
                "explanation": "Cycle detection identifies circular dependencies in graphs",
                "time_complexity": "O(V + E) for DFS-based detection",
                "space_complexity": "O(V) for visited tracking"
            },
            
            "minimum_spanning_tree": {
                "code": '''
def find_parent(parent, vertex):
    """Find parent with path compression for Union-Find."""
    if parent[vertex] != vertex:
        parent[vertex] = find_parent(parent, parent[vertex])
    return parent[vertex]

def union_sets(parent, rank, u, v):
    """Union two sets by rank for Union-Find."""
    root_u = find_parent(parent, u)
    root_v = find_parent(parent, v)
    
    if rank[root_u] < rank[root_v]:
        parent[root_u] = root_v
    elif rank[root_u] > rank[root_v]:
        parent[root_v] = root_u
    else:
        parent[root_v] = root_u
        rank[root_u] += 1

def kruskal_mst(graph):
    """Kruskal's algorithm for Minimum Spanning Tree."""
    # Get all edges and sort by weight
    edges = []
    for u in graph.vertices:
        for v, weight in graph.graph[u]:
            if u < v:  # Avoid duplicate edges in undirected graph
                edges.append((weight, u, v))
    
    edges.sort()
    print(f"Edges sorted by weight: {edges}")
    
    # Initialize Union-Find
    parent = {vertex: vertex for vertex in graph.vertices}
    rank = {vertex: 0 for vertex in graph.vertices}
    
    mst_edges = []
    total_weight = 0
    
    print("\\nKruskal's MST construction:")
    
    for weight, u, v in edges:
        if find_parent(parent, u) != find_parent(parent, v):
            union_sets(parent, rank, u, v)
            mst_edges.append((u, v, weight))
            total_weight += weight
            print(f"  Added edge ({u}, {v}) with weight {weight}")
        else:
            print(f"  Skipped edge ({u}, {v}) - would create cycle")
    
    return mst_edges, total_weight

def prim_mst(graph, start):
    """Prim's algorithm for Minimum Spanning Tree."""
    mst_edges = []
    total_weight = 0
    visited = {start}
    
    # Priority queue: (weight, u, v)
    pq = []
    for neighbor, weight in graph.graph[start]:
        heapq.heappush(pq, (weight, start, neighbor))
    
    print(f"Prim's MST starting from {start}:")
    
    while pq and len(visited) < len(graph.vertices):
        weight, u, v = heapq.heappop(pq)
        
        if v in visited:
            continue
        
        # Add vertex to MST
        visited.add(v)
        mst_edges.append((u, v, weight))
        total_weight += weight
        print(f"  Added edge ({u}, {v}) with weight {weight}")
        
        # Add new edges to priority queue
        for neighbor, edge_weight in graph.graph[v]:
            if neighbor not in visited:
                heapq.heappush(pq, (edge_weight, v, neighbor))
    
    return mst_edges, total_weight

# Example usage
print("=== Minimum Spanning Tree ===")
mst_graph = Graph(directed=False)
mst_edges = [
    ('A', 'B', 4), ('A', 'H', 8),
    ('B', 'C', 8), ('B', 'H', 11),
    ('C', 'D', 7), ('C', 'F', 4), ('C', 'I', 2),
    ('D', 'E', 9), ('D', 'F', 14),
    ('E', 'F', 10),
    ('F', 'G', 2),
    ('G', 'H', 1), ('G', 'I', 6),
    ('H', 'I', 7)
]

for u, v, w in mst_edges:
    mst_graph.add_edge(u, v, w)

kruskal_result, kruskal_weight = kruskal_mst(mst_graph)
print(f"\\nKruskal MST total weight: {kruskal_weight}")
print(f"MST edges: {kruskal_result}")

prim_result, prim_weight = prim_mst(mst_graph, 'A')
print(f"\\nPrim MST total weight: {prim_weight}")
print(f"MST edges: {prim_result}")
''',
                "explanation": "MST algorithms find minimum cost to connect all vertices",
                "time_complexity": "O(E log E) for Kruskal, O(E log V) for Prim",
                "space_complexity": "O(V) for Union-Find or priority queue"
            },
            
            "strongly_connected_components": {
                "code": '''
def kosaraju_scc(graph):
    """Kosaraju's algorithm for strongly connected components."""
    if not graph.directed:
        raise ValueError("SCC only applies to directed graphs")
    
    # Step 1: Perform DFS and store vertices by finish time
    visited = set()
    finish_stack = []
    
    def dfs1(vertex):
        visited.add(vertex)
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                dfs1(neighbor)
        finish_stack.append(vertex)
    
    print("Step 1: DFS on original graph")
    for vertex in graph.vertices:
        if vertex not in visited:
            dfs1(vertex)
    
    print(f"Finish order: {finish_stack}")
    
    # Step 2: Create transpose graph
    transpose = Graph(directed=True)
    for vertex in graph.vertices:
        transpose.vertices.add(vertex)
    
    for u in graph.vertices:
        for v, weight in graph.graph[u]:
            transpose.add_edge(v, u, weight)
    
    # Step 3: DFS on transpose in reverse finish order
    visited = set()
    scc_list = []
    
    def dfs2(vertex, current_scc):
        visited.add(vertex)
        current_scc.append(vertex)
        for neighbor, _ in transpose.graph[vertex]:
            if neighbor not in visited:
                dfs2(neighbor, current_scc)
    
    print("\\nStep 2: DFS on transpose graph")
    while finish_stack:
        vertex = finish_stack.pop()
        if vertex not in visited:
            current_scc = []
            dfs2(vertex, current_scc)
            scc_list.append(current_scc)
            print(f"Found SCC: {current_scc}")
    
    return scc_list

def tarjan_scc(graph):
    """Tarjan's algorithm for strongly connected components."""
    if not graph.directed:
        raise ValueError("SCC only applies to directed graphs")
    
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    scc_list = []
    
    def strongconnect(vertex):
        index[vertex] = index_counter[0]
        lowlinks[vertex] = index_counter[0]
        index_counter[0] += 1
        stack.append(vertex)
        on_stack[vertex] = True
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in index:
                strongconnect(neighbor)
                lowlinks[vertex] = min(lowlinks[vertex], lowlinks[neighbor])
            elif on_stack[neighbor]:
                lowlinks[vertex] = min(lowlinks[vertex], index[neighbor])
        
        # If vertex is a root node, pop the stack and create SCC
        if lowlinks[vertex] == index[vertex]:
            current_scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                current_scc.append(w)
                if w == vertex:
                    break
            scc_list.append(current_scc)
            print(f"Found SCC: {current_scc}")
    
    print("Tarjan's algorithm:")
    for vertex in graph.vertices:
        if vertex not in index:
            strongconnect(vertex)
    
    return scc_list

# Example usage
print("=== Strongly Connected Components ===")
scc_graph = Graph(directed=True)
scc_edges = [
    ('A', 'B'), ('B', 'C'), ('C', 'A'),  # SCC 1
    ('B', 'D'), ('D', 'E'), ('E', 'D'),  # SCC 2
    ('E', 'F')                           # SCC 3
]

for u, v in scc_edges:
    scc_graph.add_edge(u, v)

kosaraju_result = kosaraju_scc(scc_graph)
print(f"\\nKosaraju SCCs: {kosaraju_result}")

tarjan_result = tarjan_scc(scc_graph)
print(f"Tarjan SCCs: {tarjan_result}")
''',
                "explanation": "SCC algorithms find maximal sets of mutually reachable vertices",
                "time_complexity": "O(V + E) for both Kosaraju and Tarjan",
                "space_complexity": "O(V) for auxiliary data structures"
            }
        }
    
    def demonstrate_graph_comparison(self):
        """Compare different graph algorithms."""
        print("=== Graph Algorithms Comparison ===")
        
        # Create test graph
        graph = Graph()
        edges = [
            ('A', 'B', 4), ('A', 'C', 2),
            ('B', 'C', 1), ('B', 'D', 5),
            ('C', 'D', 8), ('C', 'E', 10),
            ('D', 'E', 2)
        ]
        
        for u, v, w in edges:
            graph.add_edge(u, v, w)
        
        start_vertex = 'A'
        
        # BFS traversal
        visited = set()
        queue = deque([start_vertex])
        bfs_order = []
        
        while queue:
            vertex = queue.popleft()
            if vertex not in visited:
                visited.add(vertex)
                bfs_order.append(vertex)
                for neighbor, _ in graph.graph[vertex]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        print(f"BFS from {start_vertex}: {bfs_order}")
        
        # Dijkstra's shortest paths
        distances = {vertex: float('inf') for vertex in graph.vertices}
        distances[start_vertex] = 0
        pq = [(0, start_vertex)]
        visited = set()
        
        while pq:
            current_dist, current_vertex = heapq.heappop(pq)
            if current_vertex in visited:
                continue
            visited.add(current_vertex)
            
            for neighbor, weight in graph.graph[current_vertex]:
                if neighbor not in visited:
                    new_distance = current_dist + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        heapq.heappush(pq, (new_distance, neighbor))
        
        print(f"Shortest distances from {start_vertex}:")
        for vertex, distance in sorted(distances.items()):
            print(f"  To {vertex}: {distance}")
    
    def get_algorithm_comparison(self) -> Dict[str, Any]:
        """Get comparison of graph algorithms."""
        return {
            "traversal": {
                "bfs": {
                    "use_case": "Shortest path in unweighted graphs, level-order traversal",
                    "time": "O(V + E)",
                    "space": "O(V)"
                },
                "dfs": {
                    "use_case": "Topological sort, cycle detection, pathfinding",
                    "time": "O(V + E)",
                    "space": "O(V)"
                }
            },
            "shortest_path": {
                "dijkstra": {
                    "use_case": "Single-source shortest path with non-negative weights",
                    "time": "O((V + E) log V)",
                    "space": "O(V)"
                },
                "floyd_warshall": {
                    "use_case": "All-pairs shortest path, works with negative weights",
                    "time": "O(V³)",
                    "space": "O(V²)"
                },
                "bellman_ford": {
                    "use_case": "Single-source with negative weights, cycle detection",
                    "time": "O(VE)",
                    "space": "O(V)"
                }
            },
            "mst": {
                "kruskal": {
                    "use_case": "Sparse graphs, when edges are pre-sorted",
                    "time": "O(E log E)",
                    "space": "O(V)"
                },
                "prim": {
                    "use_case": "Dense graphs, when starting from specific vertex",
                    "time": "O(E log V)",
                    "space": "O(V)"
                }
            }
        }
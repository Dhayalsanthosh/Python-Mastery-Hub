"""
Dijkstra's Algorithm Exercise - Comprehensive implementation with analysis and variations.
"""

import heapq
import time
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from ..base import AlgorithmDemo


class WeightedGraph:
    """Helper class for weighted graph representation."""
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.vertices = set()
    
    def add_edge(self, u, v, weight):
        """Add weighted edge to graph."""
        if weight < 0:
            raise ValueError("Dijkstra's algorithm doesn't work with negative weights")
        
        self.graph[u].append((v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def print_graph(self):
        """Print graph representation."""
        print("Graph adjacency list:")
        for vertex in sorted(self.vertices):
            neighbors = [f"{neighbor}({weight})" for neighbor, weight in self.graph[vertex]]
            print(f"  {vertex}: {neighbors}")


class DijkstraExercise(AlgorithmDemo):
    """Comprehensive Dijkstra's algorithm exercise with multiple implementations."""
    
    def __init__(self):
        super().__init__("dijkstra_exercise")
    
    def _setup_examples(self) -> None:
        """Setup Dijkstra exercise examples."""
        self.examples = {
            "basic_dijkstra": {
                "code": self._get_basic_dijkstra_code(),
                "explanation": "Basic Dijkstra's algorithm with priority queue",
                "time_complexity": "O((V + E) log V) with binary heap",
                "space_complexity": "O(V) for distances and priority queue"
            },
            "dijkstra_with_path": {
                "code": self._get_dijkstra_with_path_code(),
                "explanation": "Dijkstra with path reconstruction",
                "time_complexity": "O((V + E) log V)",
                "space_complexity": "O(V) for distances, previous, and priority queue"
            },
            "advanced_dijkstra": {
                "code": self._get_advanced_dijkstra_code(),
                "explanation": "Advanced features: all paths, early termination, bidirectional",
                "time_complexity": "Varies by optimization",
                "space_complexity": "O(V) to O(V²) depending on features"
            }
        }
    
    def _get_basic_dijkstra_code(self) -> str:
        return '''
import heapq
from collections import defaultdict

class WeightedGraph:
    """Weighted graph for shortest path algorithms."""
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.vertices = set()
    
    def add_edge(self, u, v, weight):
        """Add weighted edge to graph."""
        if weight < 0:
            raise ValueError("Dijkstra's algorithm doesn't work with negative weights")
        
        self.graph[u].append((v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def print_graph(self):
        """Print graph representation."""
        print("Graph adjacency list:")
        for vertex in sorted(self.vertices):
            neighbors = [f"{neighbor}({weight})" for neighbor, weight in self.graph[vertex]]
            print(f"  {vertex}: {neighbors}")

def dijkstra_basic(graph, start):
    """Basic Dijkstra's algorithm implementation."""
    if start not in graph.vertices:
        raise ValueError(f"Start vertex {start} not in graph")
    
    # Initialize distances and visited set
    distances = {vertex: float('inf') for vertex in graph.vertices}
    distances[start] = 0
    visited = set()
    
    # Priority queue: (distance, vertex)
    pq = [(0, start)]
    
    print(f"Dijkstra's algorithm starting from {start}")
    print(f"Initial distances: {dict(distances)}")
    print("\\nAlgorithm steps:")
    
    step = 0
    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        
        # Skip if already visited (duplicate in priority queue)
        if current_vertex in visited:
            print(f"  Step {step}: Skipping {current_vertex} (already visited)")
            continue
        
        step += 1
        visited.add(current_vertex)
        print(f"  Step {step}: Visit {current_vertex} (distance: {current_dist})")
        
        # Update distances to neighbors
        for neighbor, weight in graph.graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    old_distance = distances[neighbor]
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor))
                    print(f"    Updated {neighbor}: {old_distance} → {new_distance}")
                else:
                    print(f"    No update for {neighbor}: {new_distance} >= {distances[neighbor]}")
        
        print(f"    Current distances: {dict(distances)}")
        print(f"    Priority queue size: {len(pq)}")
    
    print(f"\\nFinal distances from {start}: {dict(distances)}")
    return distances

# Example usage
def create_sample_graph():
    """Create a sample weighted graph for testing."""
    graph = WeightedGraph()
    edges = [
        ('A', 'B', 4), ('A', 'C', 2),
        ('B', 'C', 1), ('B', 'D', 5),
        ('C', 'D', 8), ('C', 'E', 10),
        ('D', 'E', 2), ('D', 'F', 6),
        ('E', 'F', 3)
    ]
    
    for u, v, w in edges:
        graph.add_edge(u, v, w)
    
    return graph

# Test the implementation
graph = create_sample_graph()
graph.print_graph()

print("\\n" + "="*50)
distances = dijkstra_basic(graph, 'A')
'''
    
    def _get_dijkstra_with_path_code(self) -> str:
        return '''
def dijkstra_with_path(graph, start):
    """Dijkstra's algorithm with path reconstruction."""
    if start not in graph.vertices:
        raise ValueError(f"Start vertex {start} not in graph")
    
    # Initialize distances and previous vertices
    distances = {vertex: float('inf') for vertex in graph.vertices}
    previous = {vertex: None for vertex in graph.vertices}
    distances[start] = 0
    visited = set()
    
    # Priority queue: (distance, vertex)
    pq = [(0, start)]
    
    print(f"Dijkstra with path reconstruction from {start}")
    
    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        
        if current_vertex in visited:
            continue
        
        visited.add(current_vertex)
        print(f"\\nVisiting {current_vertex} (distance: {current_dist})")
        
        # Update distances to neighbors
        for neighbor, weight in graph.graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (new_distance, neighbor))
                    print(f"  Updated {neighbor}: distance = {new_distance}, previous = {current_vertex}")
    
    return distances, previous

def reconstruct_path(start, end, previous):
    """Reconstruct shortest path from start to end."""
    if previous[end] is None and start != end:
        return None  # No path exists
    
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    return path

def get_all_shortest_paths(graph, start):
    """Get shortest paths from start to all other vertices."""
    distances, previous = dijkstra_with_path(graph, start)
    paths = {}
    
    print(f"\\nShortest paths from {start}:")
    
    for vertex in sorted(graph.vertices):
        if distances[vertex] != float('inf'):
            path = reconstruct_path(start, vertex, previous)
            paths[vertex] = (path, distances[vertex])
            
            if vertex == start:
                print(f"  To {vertex}: distance = 0, path = [{vertex}]")
            else:
                path_str = " → ".join(path)
                print(f"  To {vertex}: distance = {distances[vertex]}, path = {path_str}")
        else:
            print(f"  To {vertex}: No path exists")
    
    return paths

def dijkstra_single_target(graph, start, target):
    """Optimized Dijkstra for single target with early termination."""
    distances = {vertex: float('inf') for vertex in graph.vertices}
    previous = {vertex: None for vertex in graph.vertices}
    distances[start] = 0
    visited = set()
    
    pq = [(0, start)]
    
    print(f"Finding shortest path from {start} to {target} (early termination)")
    
    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        
        if current_vertex in visited:
            continue
        
        visited.add(current_vertex)
        print(f"  Visiting {current_vertex} (distance: {current_dist})")
        
        # Early termination if we reached the target
        if current_vertex == target:
            print(f"  Reached target {target}! Terminating early.")
            break
        
        # Update distances to neighbors
        for neighbor, weight in graph.graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (new_distance, neighbor))
    
    path = reconstruct_path(start, target, previous)
    distance = distances[target]
    
    if path:
        path_str = " → ".join(path)
        print(f"\\nShortest path: {path_str}")
        print(f"Distance: {distance}")
    else:
        print(f"\\nNo path from {start} to {target}")
    
    return path, distance

# Example usage
graph = create_sample_graph()

print("=== Dijkstra with Path Reconstruction ===")
all_paths = get_all_shortest_paths(graph, 'A')

print("\\n=== Single Target with Early Termination ===")
path, distance = dijkstra_single_target(graph, 'A', 'F')
'''
    
    def _get_advanced_dijkstra_code(self) -> str:
        return '''
def dijkstra_all_shortest_paths(graph, start):
    """Find all shortest paths (when multiple paths have same length)."""
    distances = {vertex: float('inf') for vertex in graph.vertices}
    all_previous = {vertex: [] for vertex in graph.vertices}
    distances[start] = 0
    visited = set()
    
    pq = [(0, start)]
    
    print(f"Finding all shortest paths from {start}")
    
    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        
        if current_vertex in visited:
            continue
        
        visited.add(current_vertex)
        
        for neighbor, weight in graph.graph[current_vertex]:
            if neighbor not in visited:
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    # Found a shorter path
                    distances[neighbor] = new_distance
                    all_previous[neighbor] = [current_vertex]
                    heapq.heappush(pq, (new_distance, neighbor))
                elif new_distance == distances[neighbor]:
                    # Found another path of same length
                    all_previous[neighbor].append(current_vertex)
    
    return distances, all_previous

def get_all_paths_to_vertex(start, end, all_previous):
    """Generate all shortest paths from start to end."""
    if not all_previous[end] and start != end:
        return []
    
    if start == end:
        return [[start]]
    
    all_paths = []
    for prev_vertex in all_previous[end]:
        prev_paths = get_all_paths_to_vertex(start, prev_vertex, all_previous)
        for path in prev_paths:
            all_paths.append(path + [end])
    
    return all_paths

def bidirectional_dijkstra(graph, start, target):
    """Bidirectional Dijkstra for faster pathfinding."""
    # Forward search from start
    forward_dist = {vertex: float('inf') for vertex in graph.vertices}
    forward_prev = {vertex: None for vertex in graph.vertices}
    forward_visited = set()
    forward_pq = [(0, start)]
    forward_dist[start] = 0
    
    # Backward search from target (need reverse graph)
    reverse_graph = defaultdict(list)
    for u in graph.vertices:
        for v, weight in graph.graph[u]:
            reverse_graph[v].append((u, weight))
    
    backward_dist = {vertex: float('inf') for vertex in graph.vertices}
    backward_prev = {vertex: None for vertex in graph.vertices}
    backward_visited = set()
    backward_pq = [(0, target)]
    backward_dist[target] = 0
    
    shortest_distance = float('inf')
    meeting_point = None
    
    print(f"Bidirectional Dijkstra from {start} to {target}")
    
    while forward_pq or backward_pq:
        # Forward step
        if forward_pq:
            f_dist, f_vertex = heapq.heappop(forward_pq)
            
            if f_vertex not in forward_visited:
                forward_visited.add(f_vertex)
                
                # Check if we met the backward search
                if f_vertex in backward_visited:
                    total_dist = forward_dist[f_vertex] + backward_dist[f_vertex]
                    if total_dist < shortest_distance:
                        shortest_distance = total_dist
                        meeting_point = f_vertex
                        print(f"  Meeting point: {f_vertex}, distance: {total_dist}")
                
                # Expand forward
                for neighbor, weight in graph.graph[f_vertex]:
                    new_dist = f_dist + weight
                    if new_dist < forward_dist[neighbor]:
                        forward_dist[neighbor] = new_dist
                        forward_prev[neighbor] = f_vertex
                        heapq.heappush(forward_pq, (new_dist, neighbor))
        
        # Backward step
        if backward_pq:
            b_dist, b_vertex = heapq.heappop(backward_pq)
            
            if b_vertex not in backward_visited:
                backward_visited.add(b_vertex)
                
                # Check if we met the forward search
                if b_vertex in forward_visited:
                    total_dist = forward_dist[b_vertex] + backward_dist[b_vertex]
                    if total_dist < shortest_distance:
                        shortest_distance = total_dist
                        meeting_point = b_vertex
                        print(f"  Meeting point: {b_vertex}, distance: {total_dist}")
                
                # Expand backward
                for neighbor, weight in reverse_graph[b_vertex]:
                    new_dist = b_dist + weight
                    if new_dist < backward_dist[neighbor]:
                        backward_dist[neighbor] = new_dist
                        backward_prev[neighbor] = b_vertex
                        heapq.heappush(backward_pq, (new_dist, neighbor))
    
    # Reconstruct path
    if meeting_point is not None:
        # Forward path
        forward_path = []
        current = meeting_point
        while current is not None:
            forward_path.append(current)
            current = forward_prev[current]
        forward_path.reverse()
        
        # Backward path
        backward_path = []
        current = backward_prev[meeting_point]
        while current is not None:
            backward_path.append(current)
            current = backward_prev[current]
        
        full_path = forward_path + backward_path
        return full_path, shortest_distance
    
    return None, float('inf')

def dijkstra_with_constraints(graph, start, max_distance=None, forbidden_vertices=None):
    """Dijkstra with distance and vertex constraints."""
    if forbidden_vertices is None:
        forbidden_vertices = set()
    
    distances = {vertex: float('inf') for vertex in graph.vertices}
    previous = {vertex: None for vertex in graph.vertices}
    distances[start] = 0
    visited = set()
    
    pq = [(0, start)]
    
    print(f"Constrained Dijkstra from {start}")
    if max_distance:
        print(f"  Max distance: {max_distance}")
    if forbidden_vertices:
        print(f"  Forbidden vertices: {forbidden_vertices}")
    
    while pq:
        current_dist, current_vertex = heapq.heappop(pq)
        
        if current_vertex in visited or current_vertex in forbidden_vertices:
            continue
        
        if max_distance and current_dist > max_distance:
            continue
        
        visited.add(current_vertex)
        
        for neighbor, weight in graph.graph[current_vertex]:
            if neighbor not in visited and neighbor not in forbidden_vertices:
                new_distance = current_dist + weight
                
                if max_distance and new_distance > max_distance:
                    continue
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (new_distance, neighbor))
    
    # Filter results based on constraints
    reachable = {v: d for v, d in distances.items() 
                if d != float('inf') and (not max_distance or d <= max_distance)}
    
    print(f"  Reachable vertices: {dict(reachable)}")
    return reachable, previous

# Example usage of advanced features
graph = create_sample_graph()

print("=== All Shortest Paths ===")
distances, all_prev = dijkstra_all_shortest_paths(graph, 'A')

# Show all paths to a specific vertex
target = 'F'
all_paths = get_all_paths_to_vertex('A', target, all_prev)
print(f"\\nAll shortest paths from A to {target}:")
for i, path in enumerate(all_paths, 1):
    print(f"  Path {i}: {' → '.join(path)}")

print("\\n=== Bidirectional Dijkstra ===")
path, distance = bidirectional_dijkstra(graph, 'A', 'F')
if path:
    print(f"Path: {' → '.join(path)}")
    print(f"Distance: {distance}")

print("\\n=== Constrained Dijkstra ===")
reachable, _ = dijkstra_with_constraints(graph, 'A', max_distance=6, forbidden_vertices={'C'})
'''
    
    def demonstrate_dijkstra_analysis(self):
        """Comprehensive analysis of Dijkstra's algorithm."""
        print("=== Dijkstra's Algorithm Analysis ===")
        
        def create_test_graphs():
            """Create different types of graphs for testing."""
            graphs = {}
            
            # Dense graph
            dense = WeightedGraph()
            vertices = ['A', 'B', 'C', 'D', 'E']
            for i, u in enumerate(vertices):
                for j, v in enumerate(vertices):
                    if i != j:
                        dense.add_edge(u, v, abs(i - j) + 1)
            graphs['Dense'] = dense
            
            # Sparse graph
            sparse = WeightedGraph()
            sparse_edges = [('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 3), ('D', 'E', 4)]
            for u, v, w in sparse_edges:
                sparse.add_edge(u, v, w)
            graphs['Sparse'] = sparse
            
            # Grid graph
            grid = WeightedGraph()
            for i in range(3):
                for j in range(3):
                    current = f"{i},{j}"
                    if i < 2:  # Connect downward
                        grid.add_edge(current, f"{i+1},{j}", 1)
                    if j < 2:  # Connect rightward
                        grid.add_edge(current, f"{i},{j+1}", 1)
            graphs['Grid'] = grid
            
            return graphs
        
        def time_dijkstra(graph, start):
            """Time Dijkstra's algorithm execution."""
            distances = {vertex: float('inf') for vertex in graph.vertices}
            distances[start] = 0
            visited = set()
            pq = [(0, start)]
            
            start_time = time.time()
            
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
            
            end_time = time.time()
            return (end_time - start_time) * 1000, distances
        
        graphs = create_test_graphs()
        
        for graph_type, graph in graphs.items():
            print(f"\n{graph_type} Graph Analysis:")
            print(f"  Vertices: {len(graph.vertices)}")
            edge_count = sum(len(neighbors) for neighbors in graph.graph.values())
            print(f"  Edges: {edge_count}")
            
            # Time the algorithm
            start_vertex = list(graph.vertices)[0]
            exec_time, distances = time_dijkstra(graph, start_vertex)
            
            print(f"  Execution time: {exec_time:.3f}ms")
            finite_distances = [d for d in distances.values() if d != float('inf')]
            if finite_distances:
                avg_distance = sum(finite_distances) / len(finite_distances)
                print(f"  Average distance: {avg_distance:.2f}")
    
    def get_exercise_tasks(self) -> List[str]:
        """Get list of exercise tasks for students."""
        return [
            "Implement basic Dijkstra's algorithm with priority queue",
            "Add path reconstruction to return actual shortest paths",
            "Implement early termination for single target queries",
            "Add support for multiple shortest paths of equal length",
            "Implement bidirectional Dijkstra for faster pathfinding",
            "Add constraints (max distance, forbidden vertices)",
            "Compare performance with other shortest path algorithms",
            "Handle edge cases (disconnected graphs, negative weights)",
            "Implement A* algorithm as extension of Dijkstra",
            "Apply algorithm to real-world problems (GPS navigation, network routing)"
        ]
    
    def get_starter_code(self) -> str:
        """Get starter code template for students."""
        return '''
import heapq
from collections import defaultdict

class WeightedGraph:
    """Weighted graph implementation."""
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.vertices = set()
    
    def add_edge(self, u, v, weight):
        """Add weighted edge to graph."""
        # TODO: Add input validation
        # TODO: Update graph structure
        pass
    
    def get_neighbors(self, vertex):
        """Get neighbors of a vertex."""
        # TODO: Return neighbors with weights
        pass

def dijkstra(graph, start):
    """
    Implement Dijkstra's shortest path algorithm.
    
    Args:
        graph: WeightedGraph instance
        start: Starting vertex
    
    Returns:
        Dictionary of shortest distances from start to all vertices
    """
    # TODO: Initialize data structures
    # TODO: Implement main algorithm loop
    # TODO: Return results
    pass

def dijkstra_with_path(graph, start):
    """
    Dijkstra with path reconstruction.
    
    Args:
        graph: WeightedGraph instance
        start: Starting vertex
    
    Returns:
        Tuple of (distances, previous) for path reconstruction
    """
    # TODO: Implement with path tracking
    pass

def reconstruct_path(start, end, previous):
    """
    Reconstruct shortest path from previous array.
    
    Args:
        start: Starting vertex
        end: Ending vertex  
        previous: Previous vertex mapping
    
    Returns:
        List representing the shortest path, or None if no path exists
    """
    # TODO: Reconstruct path from end to start
    pass

def dijkstra_single_target(graph, start, target):
    """
    Optimized Dijkstra for single target with early termination.
    
    Args:
        graph: WeightedGraph instance
        start: Starting vertex
        target: Target vertex
    
    Returns:
        Tuple of (path, distance)
    """
    # TODO: Implement with early termination
    pass

# Test your implementation
if __name__ == "__main__":
    # Create test graph
    graph = WeightedGraph()
    edges = [
        ('A', 'B', 4), ('A', 'C', 2),
        ('B', 'C', 1), ('B', 'D', 5),
        ('C', 'D', 8), ('C', 'E', 10),
        ('D', 'E', 2)
    ]
    
    for u, v, w in edges:
        graph.add_edge(u, v, w)
    
    print("Testing Dijkstra implementations:")
    
    # Test basic Dijkstra
    distances = dijkstra(graph, 'A')
    print(f"Distances from A: {distances}")
    
    # Test with path reconstruction
    distances, previous = dijkstra_with_path(graph, 'A')
    for vertex in graph.vertices:
        if vertex != 'A':
            path = reconstruct_path('A', vertex, previous)
            if path:
                print(f"Path to {vertex}: {' → '.join(path)} (distance: {distances[vertex]})")
    
    # Test single target
    path, distance = dijkstra_single_target(graph, 'A', 'E')
    if path:
        print(f"Shortest path A → E: {' → '.join(path)} (distance: {distance})")
'''
    
    def validate_solution(self, student_dijkstra_func) -> Tuple[bool, List[str]]:
        """Validate student's Dijkstra implementation."""
        # Create test graph
        graph = WeightedGraph()
        edges = [
            ('A', 'B', 4), ('A', 'C', 2),
            ('B', 'C', 1), ('B', 'D', 5),
            ('C', 'D', 8), ('C', 'E', 10),
            ('D', 'E', 2)
        ]
        
        for u, v, w in edges:
            graph.add_edge(u, v, w)
        
        expected_distances = {
            'A': {'A': 0, 'B': 3, 'C': 2, 'D': 8, 'E': 10},
            'B': {'A': float('inf'), 'B': 0, 'C': 1, 'D': 5, 'E': 7},
            'D': {'A': float('inf'), 'B': float('inf'), 'C': float('inf'), 'D': 0, 'E': 2}
        }
        
        feedback = []
        all_passed = True
        
        for start_vertex, expected in expected_distances.items():
            try:
                result = student_dijkstra_func(graph, start_vertex)
                
                if result == expected:
                    feedback.append(f"✓ Test from {start_vertex} passed")
                else:
                    feedback.append(f"✗ Test from {start_vertex} failed")
                    feedback.append(f"  Expected: {expected}")
                    feedback.append(f"  Got: {result}")
                    all_passed = False
                    
            except Exception as e:
                feedback.append(f"✗ Test from {start_vertex} raised exception: {str(e)}")
                all_passed = False
        
        return all_passed, feedback
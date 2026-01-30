"""
Advanced Algorithmic Challenges - Hackathon/Olympiad Level
Contains intentional bugs in complex algorithms
"""

def longest_common_subsequence(s1: str, s2: str) -> int:
    """
    Find length of longest common subsequence using dynamic programming.
    
    Bug: Wrong DP recurrence relation
    """
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                # BUG: Should be max(dp[i-1][j], dp[i][j-1])
                dp[i][j] = dp[i - 1][j - 1]  # Wrong!
    
    return dp[n][m]


def dijkstra_shortest_path(graph: dict[int, list[tuple[int, int]]], start: int, end: int) -> int:
    """
    Dijkstra's algorithm for shortest path in weighted graph.
    
    Bug: Using regular queue instead of priority queue
    """
    import sys
    from collections import deque
    
    distances = {node: sys.maxsize for node in graph}
    distances[start] = 0
    
    # BUG: Should use heapq (priority queue), not deque (FIFO)
    queue = deque([start])
    visited = set()
    
    while queue:
        current = queue.popleft()  # Wrong: not extracting min!
        
        if current in visited:
            continue
        visited.add(current)
        
        if current == end:
            return distances[end]
        
        for neighbor, weight in graph.get(current, []):
            distance = distances[current] + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                queue.append(neighbor)
    
    return distances[end] if distances[end] != sys.maxsize else -1


def knapsack_01(weights: list[int], values: list[int], capacity: int) -> int:
    """
    0/1 Knapsack problem using dynamic programming.
    
    Bug: Wrong dimension initialization
    """
    n = len(weights)
    # BUG: Should be dp[n+1][capacity+1], wrong dimension order
    dp = [[0] * (n + 1) for _ in range(capacity + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                # BUG: Indices swapped (should be dp[i-1][w])
                dp[w][i] = max(
                    values[i - 1] + dp[w - weights[i - 1]][i - 1],
                    dp[w][i - 1]
                )
            else:
                dp[w][i] = dp[w][i - 1]
    
    return dp[capacity][n]


def topological_sort(graph: dict[int, list[int]]) -> list[int]:
    """
    Topological sort using DFS (Kahn's algorithm variant).
    
    Bug: Missing cycle detection
    """
    visited = set()
    stack = []
    
    def dfs(node):
        # BUG: No cycle detection - will infinite loop on cyclic graphs!
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(node)
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return stack[::-1]


if __name__ == "__main__":
    # Test LCS
    print("LCS('ABCBDAB', 'BDCABA'):", longest_common_subsequence('ABCBDAB', 'BDCABA'))  # Should be 4
    
    # Test Dijkstra
    graph = {
        0: [(1, 4), (2, 1)],
        1: [(3, 1)],
        2: [(1, 2), (3, 5)],
        3: []
    }
    print("Shortest path 0->3:", dijkstra_shortest_path(graph, 0, 3))  # Should be 4
    
    # Test Knapsack
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 5
    print("Knapsack max value:", knapsack_01(weights, values, capacity))  # Should be 7
    
    # Test Topological Sort
    dag = {0: [1, 2], 1: [3], 2: [3], 3: []}
    print("Topological order:", topological_sort(dag))  # Should be [0, 2, 1, 3] or similar

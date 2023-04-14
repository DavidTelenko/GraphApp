def deleteNode(adjacencyList, node):
    if node not in adjacencyList:
        return

    for vertex in adjacencyList:
        if node in adjacencyList[vertex]:
            del adjacencyList[vertex][node]

    del adjacencyList[node]


def renameNode(adjacencyList, oldId, newId):
    if oldId not in adjacencyList:
        return False
    if newId in adjacencyList:
        return False

    newNode = adjacencyList[oldId]

    del adjacencyList[oldId]

    adjacencyList[newId] = newNode

    for node in adjacencyList:
        if oldId in adjacencyList[node]:
            adjacencyList[node][newId] = adjacencyList[node][oldId]
            del adjacencyList[node][oldId]

    return True


def reweightEdge(adjacencyList, id1, id2, newWeight):
    if id1 not in adjacencyList or id2 not in adjacencyList:
        return

    if id2 in adjacencyList[id1]:
        adjacencyList[id1][id2] = newWeight

    if id1 in adjacencyList[id2]:
        adjacencyList[id2][id1] = newWeight


def deleteEdge(adjacencyList, id1, id2):
    if id1 not in adjacencyList or id2 not in adjacencyList:
        return

    if id2 in adjacencyList[id1]:
        del adjacencyList[id1][id2]

    if id1 in adjacencyList[id2]:
        del adjacencyList[id2][id1]


def remap(n, start1, stop1, start2, stop2, withinBounds: bool = False):
    new_val = (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

    if not withinBounds:
        return new_val

    min_val, max_val = min(start2, stop2), max(start2, stop2)
    return min(max(new_val, min_val), max_val)


def adjListToAdjMatrix(adjList):
    n = len(adjList)

    adjMatrix = [[0 for _ in range(n)] for _ in range(n)]
    idKey = dict(zip(adjList.keys(), list(range(n))))

    for vertex, edges in adjList.items():
        i = idKey[vertex]
        for edge in edges:
            j = idKey[edge]
            adjMatrix[i][j] = adjList[vertex][edge]

    return adjMatrix, idKey


def pushRelabel(graph, s, t):
    capacity, idKey = adjListToAdjMatrix(graph)
    s, t = idKey[s], idKey[t]
    n = len(graph)

    inf = float('inf')

    excessVertices = []
    height = [0] * n
    excess = [0] * n
    flow = [[0] * n for _ in range(n)]
    seen = [0] * n

    def push(u, v):
        d = min(excess[u], capacity[u][v] - flow[u][v])
        flow[u][v] += d
        flow[v][u] -= d
        excess[u] -= d
        excess[v] += d

        if (d and excess[v] == d):
            excessVertices.append(v)

    def relabel(u):
        d = inf
        for i in range(n):
            if capacity[u][i] - flow[u][i] > 0:
                d = min(d, height[i])
        if d < inf:
            height[u] = d + 1

    def discharge(u):
        while excess[u] > 0:
            if seen[u] < n:
                v = seen[u]
                if capacity[u][v] - flow[u][v] > 0 and height[u] > height[v]:
                    push(u, v)
                else:
                    seen[u] += 1
            else:
                relabel(u)
                seen[u] = 0

    height[s] = n
    excess[s] = inf

    for i in range(n):
        if i != s:
            push(s, i)

    while excessVertices:
        u = excessVertices.pop(0)
        if u != s and u != t:
            discharge(u)

    maxFlow = 0
    for i in range(n):
        maxFlow += flow[i][t]

    return maxFlow


algs = {
    "pushRelabel": pushRelabel
}


if __name__ == "__main__":
    pass

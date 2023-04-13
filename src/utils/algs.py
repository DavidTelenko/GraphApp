def deleteNode(adjacencyList, node):
    if node not in adjacencyList:
        return

    for vertex in adjacencyList:
        if node in adjacencyList[vertex]:
            del adjacencyList[vertex][node]

    del adjacencyList[node]


def renameNode(adjacencyList, oldId, newId):
    if oldId not in adjacencyList:
        return

    newNode = adjacencyList[oldId]

    del adjacencyList[oldId]

    adjacencyList[newId] = newNode

    for node in adjacencyList:
        if oldId in adjacencyList[node]:
            adjacencyList[node][newId] = adjacencyList[node][oldId]
            del adjacencyList[node][oldId]


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


def pushRelabel(graph):
    print(graph)


algs = {
    "pushRelabel": pushRelabel
}

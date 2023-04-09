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


def remap(n, start1, stop1, start2, stop2, withinBounds: bool = False):
    new_val = (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

    if not withinBounds:
        return new_val

    min_val = min(start2, stop2)
    max_val = max(start2, stop2)
    return min(max(new_val, min_val), max_val)

def calcArrow(startPoint, endPoint, w, radius=0):
    arrowHeight, arrowWidth = w * 2 + w, w * 1.5

    dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

    length = sqrt(dx ** 2 + dy ** 2)

    normX, normY = dx / length, dy / length
    perpX, perpY = -normY, normX

    offsetRadiusX, offsetRadiusY = normX * radius, normY * radius

    leftX = endPoint.x() + arrowHeight * normX + arrowWidth * perpX + offsetRadiusX
    leftY = endPoint.y() + arrowHeight * normY + arrowWidth * perpY + offsetRadiusY

    rightX = endPoint.x() + arrowHeight * normX - arrowWidth * perpX + offsetRadiusX
    rightY = endPoint.y() + arrowHeight * normY - arrowWidth * perpY + offsetRadiusY

    arrowEndPoint = QPointF(endPoint.x() + offsetRadiusX,
                            endPoint.y() + offsetRadiusY)

    point2 = QPointF(leftX, leftY)
    point3 = QPointF(rightX, rightY)

    newEndPoint = QPointF(endPoint.x() + offsetRadiusX + arrowHeight * normX,
                          endPoint.y() + offsetRadiusY + arrowHeight * normY)

    return newEndPoint, [point2, arrowEndPoint, point3]
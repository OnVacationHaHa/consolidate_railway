import math


def DBSCAN(nodes, eps, minPts):
    labels = [0] * len(nodes)
    C = 0
    for P in range(0, len(nodes)):
        if not (labels[P] == 0):
            continue
        NeighborPts = regionQuery(nodes, P, eps)
        if len(NeighborPts) < minPts:
            labels[P] = -1
        else:
            C += 1
            labels[P] = C
            growCluster(nodes, labels, P, C, eps, minPts)
    for i in range(len(labels)):
        nodes[i].cluster_id = labels[i]
    return C


def growCluster(D, labels, P, C, eps, MinPts):
    SearchQueue = [P]
    i = 0
    while i < len(SearchQueue):
        P = SearchQueue[i]
        NeighborPts = regionQuery(D, P, eps)
        if len(NeighborPts) < MinPts:
            i += 1
            continue
        for Pn in NeighborPts:
            if labels[Pn] == -1:
                labels[Pn] = C
            elif labels[Pn] == 0:
                labels[Pn] = C
                SearchQueue.append(Pn)
        i += 1


def dist(a, b):
    x_square = (a.x_location - b.x_location) ** 2
    y_square = (a.y_location - b.y_location) ** 2
    aa=math.sqrt(x_square + y_square)
    return math.sqrt(x_square + y_square)


def epsNeighbor(a, b, eps):
    return dist(a, b) < eps


def regionQuery(D, P, eps):
    neighbors = []
    for Pn in range(0, len(D)):
        if epsNeighbor(D[Pn], D[P], eps):
            neighbors.append(Pn)
    return neighbors


def getCentralNode(stationNodes, eps, minPts, segmentNodes):
    clusters_num = DBSCAN(stationNodes, eps, minPts)
    clusters = []
    noise=set()
    maxX = []
    maxY = []
    minX = []
    minY = []
    for i in range(clusters_num):
        clusters.append([])
        maxX.append(-99999)
        maxY.append(-99999)
        minX.append(99999)
        minY.append(99999)
    for node in stationNodes:
        if node.cluster_id == -1:
            noise.add(node)
            continue
        clusters[node.cluster_id - 1].append(node)
        if node.x_location > maxX[node.cluster_id - 1]:
            maxX[node.cluster_id - 1] = node.x_location
        if node.x_location < minX[node.cluster_id - 1]:
            minX[node.cluster_id - 1] = node.x_location
        if node.y_location > maxY[node.cluster_id - 1]:
            maxY[node.cluster_id - 1] = node.y_location
        if node.y_location < minY[node.cluster_id - 1]:
            minY[node.cluster_id - 1] = node.y_location
    segmentNodes=checkNode(segmentNodes, clusters, maxX, maxY, minX, minY)
    for cluster in clusters:
        xCoordSum, yCoordSum = 0, 0
        for node in cluster:
            xCoordSum += node.x_location
            yCoordSum += node.y_location
        nodeSum = len(cluster)
        aveXCoord = xCoordSum / nodeSum
        aveYCoord = yCoordSum / nodeSum
        nodeId0 = cluster[0].node_id
        for node in cluster:
            node.x_location = aveXCoord
            node.y_location = aveYCoord
            node.node_id = nodeId0
            node.is_changing=True
    return clusters,noise,segmentNodes


def checkNode(segmentNodes, clusters, maxX, maxY, minX, minY):
    delNodes = set()
    for node in segmentNodes:
        for i in range(len(clusters)):
            max_x = maxX[i]
            max_y = maxY[i]
            min_x = minX[i]
            min_y = minY[i]
            if min_x <= node.x_location <= max_x and min_y <= node.y_location <= max_y:
                clusters[i].append(node)
                delNodes.add(node)
                break
    segmentNodes_set = set(segmentNodes)
    segmentNodes = list(segmentNodes_set.difference(delNodes))
    return segmentNodes

#!/usr/bin/python

import networkx as nx
import coord
import util
import constants

PATHFINDING_DEBUG = False

class Board:

    @staticmethod
    def _xyToId(x, y):
        return x, y

    def __init__(self, HeatMap):
        if PATHFINDING_DEBUG: print "Graphing..."

        height = len(HeatMap[0])
        width = len(HeatMap)
        if PATHFINDING_DEBUG: print "height :" + str(height)
        if PATHFINDING_DEBUG: print "width :" + str(width)

        self._graph = nx.Graph()

        for x in range(0, width):
            for y in range(0, height):
                #print Board._xyToId(x, y)
                self._graph.add_node(Board._xyToId(x, y))

        # Add vertical edges
        for x in range(0, width):
            for y in range(0, height):
                curId = Board._xyToId(x, y)
                plusX = Board._xyToId(x+1, y)
                plusY = Board._xyToId(x, y+1)
                if x != width -1:
                    self._graph.add_edge(curId, plusX, weight=HeatMap[x][y] + HeatMap[x+1][y])
                if y != height -1:
                    # print(str(curId) + " to " + str(plusY))
                    self._graph.add_edge(Board._xyToId(x, y), plusY, weight=HeatMap[x][y] + HeatMap[x][y+1])

    def path(self, currentCoord, targetCoord):
        if PATHFINDING_DEBUG: print "Looking for path from x", currentCoord.x, "y", currentCoord.y, " to x", targetCoord.x, "y", targetCoord.y
        path = None

        try:
            path = nx.shortest_path(
                self._graph,
                source=Board._xyToId(currentCoord.x, currentCoord.y),
                target=Board._xyToId(targetCoord.x, targetCoord.y),
                weight='weight'
            )
        except:
            print "Failed to find any path from x", currentCoord.x, "y", currentCoord.y, " to x", targetCoord.x, "y", targetCoord.y
            return util.bad_move()

        return Path(self._graph, path)


class Path:
    def __init__(self, graph, nodeList):
        # Todo: "unreachable"
        if PATHFINDING_DEBUG: print "Nodelist:", nodeList
        self._nodes = nodeList

        self.cost = 0
        if len(nodeList) < 2:
            self.cost = 9992
            self.nextCoord = None
            self.nextDirection = "No"
            print "Path of length 1, looks impossible?"
            return

        self.length = len(nodeList)
        self.nextCoord = coord.Coord(nodeList[1][0], nodeList[1][1])
        self.nextDirection = "????"

        if self.nextCoord.x == nodeList[0][0]:
            if self.nextCoord.y < nodeList[0][1]:
                self.nextDirection = "up"
            else:
                self.nextDirection = "down"
        elif self.nextCoord.y == nodeList[0][1]:
            if self.nextCoord.x > nodeList[0][0]:
                self.nextDirection = "right"
            else:
                self.nextDirection = "left"

        weights = nx.get_edge_attributes(graph, 'weight')
        for nodeSeq in range(0, len(nodeList)-1):
            cur = nodeList[nodeSeq]
            next = nodeList[nodeSeq+1]
            if (cur, next) in weights:
                self.cost += weights[(cur, next)]
            else:
                self.cost += weights[(next, cur)]
        self.cost -= constants.ourHeadWeight
        if PATHFINDING_DEBUG: print "cost:", self.cost
    def __gt__(self, other):
        return self.cost > other.cost
    def __lt__(self, other):
        return self.cost < other.cost
    def __ge__(self, other):
        return self.cost >= other.cost
    def __le__(self, other):
        return self.cost <= other.cost

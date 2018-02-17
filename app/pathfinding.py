#!/usr/bin/python

import networkx as nx
import coord


# HOW TO USE:
# Graph = pathfinding.graphify(HeatMap)
# Then run:
# pathfinding.cheapest_path(Graph, HeightOfPlayArea, HeadPos, TargetPos)
# This returns a dict, see below for names/details


# Heatmap is an array of the board, with higher values being less safe.
# Headpos is the [column, row] of the snake head.


class Board:

    @staticmethod
    def _xyToId(x, y):
        return (x, y),

    def __init__(self, HeatMap):
        height = len(HeatMap[0])
        width = len(HeatMap)
        print "height :" + str(height)
        print "width :" + str(width)

        self._graph = nx.Graph()

        for x in range(0, width):
            print(x)
            for y in range(0, height):
                print Board._xyToId(x, y)
                self._graph.add_node(Board._xyToId(x, y))

        # Add vertical edges
        for x in range(0, width):
            for y in range(0, height):
                curId = Board._xyToId(x, y)
                plusX = Board._xyToId(x+1, y)
                plusY = Board._xyToId(x, y+1)
                if x != width -1:
                    self._graph.add_edge(curId, plusX, weight=HeatMap[x][y] + HeatMap[x+1][y])
                    print "Linked " + curId + " to " + plusX
                if y != height -1:
                    self._graph.add_edge(Board._xyToId(x, y), plusY, weight=HeatMap[x][y] + HeatMap[x][y+1])
                    print "Linked " + curId + " to " + plusY

    def path(self, currentCoord, targetCoord):
        path = nx.shortest_path(
            self._graph,
            source=Board._xyToId(currentCoord.x, currentCoord.y),
            target=Board._xyToId(targetCoord.x, targetCoord.y),
            weight='weight'
        )
        print path
        return Path(self._graph, path)


class Path:
    def __init__(self, graph, nodeList):
        self._nodes = nodeList

        self.length = len(nodeList)
        self.danger = 0
        self.nextCoord = coord.Coord(nodeList[1][0], nodeList[1][1])
        self.nextDirection = "????"
        if self.nextCoord.x == nodeList[0][0]:
            if self.nextCoord.y > nodeList[0][1]:
                self.nextCoord = "up"
            else:
                self.nextCoord = "down"
        elif self.nextCoord.y == nodeList[0][1]:
            if self.nextCoord.x > nodeList[0][0]:
                self.nextCoord = "right"
            else:
                self.nextCoord = "left"

        weights = nx.get_edge_attributes(graph, 'weight')
        print weights
        for nodeSeq in range(0, self.length-1):
            cur = nodeList[nodeSeq]
            next = nodeList[nodeSeq+1]
            if (cur, next) in weights:
                self.danger += weights[(cur, next)]
            else:
                self.danger += weights[(next, cur)]

    # def cheapest_path(self, heatmap, head_pos, target_pos, data):
    #     if not util.is_valid_move(target_pos, data):
    #         return {
    #             "path": [],
    #             "length": 0,
    #             "nextPos": head_pos,
    #             "cost": 9998
    #         }
    #     height = data['height']
    #     path = nx.shortest_path(self._graph, source =head_pos[0] * height + head_pos[1], target=target_pos[0] * height + target_pos[1], weight='weight')
    #     pos_of_next_move = [path[1] // height, path[1] % height]
    #     weight = 0
    #     for i in range(1, len(path)):
    #         weight += heatmap[path[i] // height][path[i] % height]  # Get weight of move
    #     return {
    #         "path": path,
    #         "length": len(path),
    #         "nextPos": pos_of_next_move,
    #         "cost": weight
    #     }

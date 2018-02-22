#!/usr/bin/python

import networkx as nx
import coord


class Board:

    @staticmethod
    def _xyToId(x, y):
        return (x, y),

    def __init__(self, HeatMap):
        print "Graphing..."

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
                if y != height -1:
                    self._graph.add_edge(Board._xyToId(x, y), plusY, weight=HeatMap[x][y] + HeatMap[x][y+1])

    def path(self, currentCoord, targetCoord):
        print "Looking for path from x", currentCoord.x, "y", currentCoord.y, " to x", targetCoord.x, "y", targetCoord.y
        path = nx.shortest_path(
            self._graph,
            source=Board._xyToId(currentCoord.x, currentCoord.y),
            target=Board._xyToId(targetCoord.x, targetCoord.y),
            weight='weight'
        )
        return Path(self._graph, path)


class Path:
    def __init__(self, graph, nodeList):
        # Todo: "unreachable"
        self._nodes = nodeList

        print nodeList
        self.cost = 9995
        if len(nodeList) < 2:
            return

        self.length = len(nodeList)
        self.nextCoord = coord.Coord(nodeList[1][0][0], nodeList[1][0][1])
        self.nextDirection = "????"

        if self.nextCoord.x == nodeList[0][0][0]:
            if self.nextCoord.y > nodeList[0][0][1]:
                self.nextDirection = "up"
            else:
                self.nextDirection = "down"
        elif self.nextCoord.y == nodeList[0][0][1]:
            if self.nextCoord.x > nodeList[0][0][0]:
                self.nextDirection = "right"
            else:
                self.nextDirection = "left"

        weights = nx.get_edge_attributes(graph, 'weight')
        for nodeSeq in range(0, self.length-1):
            cur = nodeList[nodeSeq]
            next = nodeList[nodeSeq+1]
            if (cur, next) in weights:
                self.cost += weights[(cur, next)]
            else:
                self.cost += weights[(next, cur)]

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

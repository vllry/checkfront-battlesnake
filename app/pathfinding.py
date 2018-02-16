#!/usr/bin/python

import networkx as nx
import util


# HOW TO USE:
# Graph = pathfinding.graphify(HeatMap)
# Then run:
# pathfinding.cheapest_path(Graph, HeightOfPlayArea, HeadPos, TargetPos)
# This returns a dict, see below for names/details


# Heatmap is an array of the board, with higher values being less safe.
# Headpos is the [column, row] of the snake head.

# RETURNS a networkx graph
def graphify(HeatMap):
    height = len(HeatMap[0])
    width = len(HeatMap)
    g = nx.Graph()

    g.add_nodes_from(range(0, height*width))

    # Add vertical edges
    for column in range(0, width):
        for row in range(0, height-1):
            cur = column*height + row
            next = cur + 1
            weight = HeatMap[column][row] + HeatMap[column][row+1]
            # print str(cur) + " Add edge between [" + str(column) + "][" + str(row) + "] and [" + str(column) + "][" + str(row+1) + "], weight=" + str(weight)
            g.add_edge(cur, next)
            g[cur][next]['weight'] = weight

    # Add horizontal edges
    for row in range(0, height):
        for column in range(0, width-1):
            cur = column*height + row
            next = cur + height
            weight = HeatMap[column][row] + HeatMap[column+1][row]
            # print str(next) + " Add edge between [" + str(column) + "][" + str(row) + "] and [" + str(column+1) + "][" + str(row) + "], weight=" + str(weight)
            g.add_edge(cur, next)
            g[cur][next]['weight'] = weight

    return g


def cheapest_path(G, heatmap, head_pos, target_pos, data):
    if not util.is_valid_move(target_pos, data):
        return {
            "path": [],
            "length": 0,
            "nextPos": head_pos,
            "cost": 9998
        }
    height = data['height']
    path = nx.shortest_path(G, source =head_pos[0] * height + head_pos[1], target=target_pos[0] * height + target_pos[1], weight='weight')
    pos_of_next_move = [path[1] // height, path[1] % height]
    weight = 0
    for i in range(1, len(path)):
        weight += heatmap[path[i] // height][path[i] % height]  # Get weight of move
    return {
        "path": path,
        "length": len(path),
        "nextPos": pos_of_next_move,
        "cost": weight
    }

import pathfinding
import coord
import networkx
import matplotlib.pyplot as plt


heatmap = [
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
]

board = pathfinding.Board(heatmap)
path = board.path(coord.Coord(0, 0), coord.Coord(4, 0))
print path.nextCoord.x, path.nextCoord.y
print path.nextDirection

#fig = plt.figure()  # Needed to set up internals in matplotlib.pyplot.
#networkx.draw_networkx(board._graph, with_labels=True)
#plt.show()

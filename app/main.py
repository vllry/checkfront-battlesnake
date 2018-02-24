import bottle
import os
import json
import coord
import random
import time
import sys

import pathfinding
from heatmap import print_heatmap, gen_heatmap
import util

taunts = ['get_Booked!', 'brought_to_you_by_Checkfront!', 'generic_Taunt!', 'zort_narf_poit_Egad!', 'you_are_not_Prepared!', 'ill_get_you_my_Pretty!', 'hiss_CamelNoise!', 'flee_Mortals!']

starvation_Limit 				= 25
starvation_Cost 				= 100
hunger_Limit 					= 50
hunger_Cost 					= 70
preferred_Snek_Length_modifer 	= -2 # ie 2 would make our snake try to get 2 longer than any other snake
greedy_food_Cost 				= 40
follow_Cost_Limit               = 200
idle_Cost_Limit 				= 100
server_Port						= '8081'
name 							= 'camel_Snake'

PRINT_REQUESTS = False

if len(sys.argv) > 2:
	starvation_Limit 				= int(sys.argv[1])   #25
	starvation_Cost 				= int(sys.argv[2])  #100
	hunger_Limit 					= int(sys.argv[3])   #50
	hunger_Cost 					= int(sys.argv[4])   #70
	preferred_Snek_Length_modifer 	= int(sys.argv[5])    #2
	greedy_food_Cost 				= int(sys.argv[6])   #40
	follow_Cost_Limit 				= int(sys.argv[7])  #200
	idle_Cost_Limit 				= int(sys.argv[8])  #100
	server_Port						= sys.argv[9] 		#8080
	name 							= sys.argv[10] #camel_snake

MAX_WIGGLE = 7

# retrieve and parse data from REST API
@bottle.route('/static/<path:path>')
def static(path):
	return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
	head_url = '%s://%s/static/head.png' % (
		bottle.request.urlparts.scheme,
		bottle.request.urlparts.netloc
	)

	return {
		'color': '#00ff00',
		'head': head_url
	}


@bottle.post('/start')
def start():
	data = bottle.request.json
	rand = random.randint(0, 2)
	taunt = taunts[rand]
	return {
		'name': name,
		'color': '#1E90FF',
		'head_url': 'https://demo.checkfront.com/images/checky.png',
		'head_type': 'smile',
		'tail_type': 'fat-rattle',
		'taunt': taunt
	}


@bottle.post('/move')
def move():
	request_data_2018 = bottle.request.json
	
	request_data = reformat_request_to_2017(request_data_2018)
	
	print "\n\n\n-======- Starting",request_data["oursnake"]["name"], "- move()"
	if PRINT_REQUESTS:
		print(json.dumps(request_data, sort_keys=True, indent=4, separators=(',',': '))) # Uncomment this to save a full game state
	
	with util.TimerPrint("-======- End of " + request_data["oursnake"]["name"] + "'s move(). Full Request Time"):
		return main_logic(request_data)

def main_logic(data):
	with util.TimerPrint("Heatmap Time"):
		heatmap = gen_heatmap(data)
	print_heatmap(heatmap)
	with util.TimerPrint("Graph Time"):
		board = pathfinding.Board(heatmap)

	rand = random.randint(0, 2)
	taunt = taunts[rand]

	move = get_move(data, data['ourhead'], heatmap, board)

	if move in data['oursnake']['coords']:
		pass  # TODO: WTF DON'T MOVE INTO OURSELF!!

	response = {
		'move': move.nextDirection
	}
	if random.randint(0, 10) == 0:
		response['taunt'] = taunt

	return response


def get_move(data, head, heatmap, board):
	# try different algorithms and pick our favourite one

	follow_move = follow(data, head, board)
	idle_move = idle(board, data, head)
	food_move = food(data, head, heatmap, board)
	print "Possible Move Thoughts: follow", follow_move.cost, "idle", idle_move.cost, "food", food_move.cost

	longestSnakeLength = 0
	for snake in data['snakes']:
		if snake['id'] != data['oursnake']['id'] and len(snake['coords']) > longestSnakeLength:
			longestSnakeLength = len(snake['coords'])

	# Worst case scenario: Go 1 square in a direction that doesn't immediately kill it
	move = move_idle_dumb(data, head, heatmap, board)
	move_name = 'default'

	if (int(data['oursnake']['health_points']) < starvation_Limit and food_move.cost < starvation_Cost):
		move = food_move
		move_name = 'food-hungry'
	elif (int(data['oursnake']['health_points']) < hunger_Limit and food_move.cost < hunger_Cost):
		move = food_move
		move_name = 'food-easy-pickings'
	elif ((longestSnakeLength + preferred_Snek_Length_modifer) >= len(data['oursnake']['coords']) and food_move.cost < greedy_food_Cost):
		move = food_move
		move_name = 'food-greedy'
	elif (follow_move.cost < follow_Cost_Limit):
		move = follow_move
		move_name = 'follow'
	elif (idle_move.cost < idle_Cost_Limit):
		move = idle_move
		move_name = 'idle'
	else:
		# Running out of options... find the longest path
		with util.TimerPrint("Wiggle time"):
			for dist in range(MAX_WIGGLE, 1, -1):
				wiggle_move = wiggle(data, board, head)
				if wiggle_move.cost < 100:
					move = wiggle_move
					move_name = 'wiggle ' + str(dist)
					break

	print "Recommend next move:", move_name, move.nextDirection, move.nextCoord, "from head:", head

	return move


def food(data, head, heatmap, board):
	best = None
	cost = 9996

	for snack in data['food']:
		path = board.path(coord.Coord(head[0], head[1]), coord.Coord(snack[0], snack[1]))
		heat = path.cost
		if heat < cost:
			best = path
			cost = heat

	if best is None or not util.is_valid_move(best, data):
		return util.bad_move()

	return best


def idle(board, data, head):
	oursnake = data['oursnake']['coords']
	if (len(oursnake) == 0):
		return util.bad_move()  # didn't find our snake, bail

	target = oursnake[-1]
	if (target == head):
		if head[1] > 1:
			target = [head[0], head[1] - 1]
		else:
			target = [head[0], head[1] + 1]
	if target in oursnake[:-1]:
		return util.bad_move()

	path = board.path(coord.Coord(head[0], head[1]), coord.Coord(target[0], target[1]))

	if path is None or not util.is_valid_move(path, data):
		return util.bad_move()

	return path

def follow(data, head, board):
	target = False

	for snake in data['snakes']:
		snake_tail = snake['coords'][-1]
		if util.dist(head, snake_tail) == 1:
			target = snake_tail

	if not target:
		# No tails nearby
		return util.bad_move()

	path = board.path(coord.Coord(head[0], head[1]), coord.Coord(target[0], target[1]))

	if path is None or not util.is_valid_move(path, data):
		return util.bad_move()

	return path


def wiggle(data, board, head, dist=5):
	best = util.bad_move()

	for x in range(-dist, dist + 1):
		for y in range(-dist, dist + 1):
			if (abs(x) + abs(y)) == dist:
				path = board.path(coord.Coord(head[0], head[1]), coord.Coord(head[0] + x, head[1] + y))
				if path.cost < best.cost and not util.is_valid_move(path, data):
					best = path

	return best

def move_idle_dumb(data, head, heatmap, board):
	left_pathdata = board.path(coord.Coord(head[0], head[1]), coord.Coord(max(0, head[0] - 1), head[1]))
	right_pathdata = board.path(coord.Coord(head[0], head[1]), coord.Coord(min(len(heatmap) - 1, head[0] + 1), head[1]))
	up_pathdata = board.path(coord.Coord(head[0], head[1]), coord.Coord(head[0], max(0, head[1] - 1)))
	down_pathdata = board.path(coord.Coord(head[0], head[1]), coord.Coord(head[0], min(len(heatmap[0]) - 1, head[1] + 1)))

	smallest = min(left_pathdata.cost, right_pathdata.cost, up_pathdata.cost, down_pathdata.cost)
	if smallest == left_pathdata.cost:
		return left_pathdata
	if smallest == right_pathdata.cost:
		return right_pathdata
	if smallest == up_pathdata.cost:
		return up_pathdata
	if smallest == down_pathdata.cost:
		return down_pathdata


def get_direction_from_target_headpos(head, move):
	if move[1] > head[1]:
		nextmove = 'down'
	elif move[1] < head[1]:
		nextmove = 'up'
	elif move[0] > head[0]:
		nextmove = 'right'
	elif move[0] < head[0]:
		nextmove = 'left'
	else:
		print "UHHHH wat are you trying to move to yourself??"
		nextmove = 'left'
	return nextmove

def reformat_request_to_2017(request_data_2018):
	request_data = request_data_2018.copy()
	request_data["snakes"] = request_data_2018["snakes"]["data"]
	request_data["food"] = [[point["x"],point["y"]] for point in request_data_2018["food"]["data"]]
	for snake in request_data["snakes"] + [request_data_2018["you"]]:
		snake["coords"] = [[point["x"],point["y"]] for point in snake["body"]["data"]]
		del snake["body"]
		snake["health_points"] = snake["health"]
		del snake["health"]
	request_data['oursnake'] = request_data["you"]
	request_data['ourhead'] = request_data["you"]["coords"][0]
	del request_data["you"]
	return request_data

@bottle.post('/end')
def end():
	data = bottle.request.json

	# TODO: Do things with data

	return {
		'taunt': 'battlesnake-python!'
	}

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
	bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', server_Port), reloader=True)



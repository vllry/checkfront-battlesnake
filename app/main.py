import bottle
import os
import json
import copy
import random
import time
import sys

import pathfinding
from heatmap import print_heatmap, gen_heatmap
import util

snake_id = ''

taunts = ['get_Booked!', 'brought_to_you_by_Checkfront!', 'generic_Taunt!', 'zort_narf_poit_Egad!', 'you_are_not_Prepared!', 'ill_get_you_my_Pretty!', 'hiss_CamelNoise!', 'flee_Mortals!']

starvation_Limit 				= 25
starvation_Cost 				= 100
hunger_Limit 					= 50
hunger_Cost 					= 70
preferred_Snek_Length_modifer 	= 0
dominace_Length 				= 0
follow_Cost_Limit               = 200
idle_Cost_Limit 				= 100
server_Port						= '8081'
name 							= 'camel_Snake'

if len(sys.argv) > 2:
	starvation_Limit 				= int(sys.argv[1])   #25
	starvation_Cost 				= int(sys.argv[2])  #100
	hunger_Limit 					= int(sys.argv[3])   #50
	hunger_Cost 					= int(sys.argv[4])   #70
	preferred_Snek_Length_modifer 	= int(sys.argv[5])    #2
	dominace_Length 				= int(sys.argv[6])   #40
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
	print "\n\n"
	data = bottle.request.json

	find_our_snake(data)
	# print(data) # Uncomment this to save a full game state
	return main_logic(data)

def main_logic(data):
	time_start_request = time.clock()

	with util.TimerPrint("Heatmap Time"):
		heatmap = gen_heatmap(data)
	with util.TimerPrint("Graph Time"):
		graph = pathfinding.graphify(heatmap)
	print_heatmap(heatmap)

	rand = random.randint(0, 2)
	taunt = taunts[rand]

	move = get_move(data, data['ourhead'], heatmap, graph)

	if move in data['oursnake']['coords']:
		pass  # TODO: WTF DON'T MOVE INTO OURSELF!!

	response = {
		'move': get_direction_from_target_headpos(data['ourhead'], move)
	}
	if random.randint(0, 10) == 0:
		response['taunt'] = taunt

	print "\nFull Request Time:", str(round((time.clock() - time_start_request) * 1000, 3)) + "ms"
	return response


def get_move(data, head, heatmap, graph):
	# try different algorithms and pick our favourite one

	follow_move, follow_cost = follow(data, head, heatmap, graph)
	idle_move, idle_cost = idle(data, head, heatmap, graph)
	food_move, food_cost = food(data, head, heatmap, graph)
	print "follow", follow_cost, "idle", idle_cost, "food", food_cost

	longestSnakeLength = 0
	for snake in data['snakes']:
		if snake['id'] != snake_id and len(snake['coords']) > longestSnakeLength:
			longestSnakeLength = len(snake['coords'])

	# Worst case scenario: Go 1 square in a direction that doesn't immediately kill it
	move = move_idle_dumb(data, head, heatmap, graph)
	move_name = 'default'

	if (int(data['oursnake']['health_points']) < starvation_Limit and food_cost < starvation_Cost):
		move = food_move
		move_name = 'food-hungry'
	elif (int(data['oursnake']['health_points']) < hunger_Limit and food_cost < hunger_Cost):
		move = food_move
		move_name = 'food-easy-pickings'
	elif ((longestSnakeLength + preferred_Snek_Length_modifer) >= len(data['oursnake']['coords']) and food_cost < dominace_Length):
		move = food_move
		move_name = 'food-dominate'
	elif (follow_cost < follow_Cost_Limit):
		move = follow_move
		move_name = 'follow'
	elif (idle_cost < idle_Cost_Limit):
		move = idle_move
		move_name = 'idle'
	else:
		# Running out of options... find the longest path
		with util.TimerPrint("Wiggle time"):
			for dist in range(MAX_WIGGLE, 1, -1):
				wiggle_move, wiggle_cost = wiggle(data, head, heatmap, graph, dist)
				if wiggle_cost < 100:
					move = wiggle_move
					move_name = 'wiggle ' + str(dist)
					break

	print head, move, move_name
	print "Recommend next move", move_name, get_direction_from_target_headpos(head, move), str(move)

	return move


def food(data, head, heatmap, graph):
	move = [0, 0]
	shortest = []
	cost = 9995
	for snack in data['food']:
		pathdata = pathfinding.cheapest_path(graph, heatmap, head, snack, data)
		#print "Food idea: ", pathdata
		nextcoord = pathdata['nextPos']
		full_shortest_path = pathdata['path']
		heat = pathdata['cost']
		if heat < cost:
			shortest = full_shortest_path
			move = nextcoord
			cost = heat

	if not util.is_valid_move(move, data):
		return util.bad_move()

	return move, cost


def idle(data, head, heatmap, graph):
	oursnake = data['oursnake']['coords']
	if (len(oursnake) == 0):
		return util.bad_move()  # didn't find our snake, bail

	target = oursnake[-1]
	if (target == head):
		return util.bad_move()

	pathdata = pathfinding.cheapest_path(graph, heatmap, head, target, data)
	move = pathdata['nextPos']
	cost = pathdata['cost']

	if not util.is_valid_move(move, data):
		return util.bad_move()

	return move, cost

def follow(data, head, heatmap, graph):
	target = False

	for snake in data['snakes']:
		snake_tail = snake['coords'][-1]
		if util.dist(head, snake_tail) == 1:
			target = snake_tail

	if not target:
		# No tails nearby
		return util.bad_move()

	pathdata = pathfinding.cheapest_path(graph, heatmap, head, target, data)
	move = pathdata['nextPos']
	cost = pathdata['cost']

	if not util.is_valid_move(move, data):
		return util.bad_move()

	return move, cost

def wiggle(data, head, heatmap, graph, dist=5):
	cost = 9000
	move = head
	for x in range(-dist, dist + 1):
		for y in range(-dist, dist + 1):
			if (abs(x) + abs(y)) == dist:
				pathdata = pathfinding.cheapest_path(graph, heatmap, head, [head[0] + x, head[1] + y], data)
				if pathdata['cost'] < cost:
					cost = pathdata['cost']
					move = pathdata['nextPos']
	return move, cost

def move_idle_dumb(data, head, heatmap, graph):
	left_pathdata = pathfinding.cheapest_path(graph, heatmap, head, [max(0, head[0] - 1), head[1]], data)
	right_pathdata = pathfinding.cheapest_path(graph, heatmap, head, [min(len(heatmap)-1, head[0] + 1), head[1]], data)
	up_pathdata = pathfinding.cheapest_path(graph, heatmap, head, [head[0], max(0, head[1] - 1)], data)
	down_pathdata = pathfinding.cheapest_path(graph, heatmap, head, [head[0], min(len(heatmap[0])-1, head[1] + 1)], data)

	smallest = min(left_pathdata['cost'], right_pathdata['cost'], up_pathdata['cost'], down_pathdata['cost'])
	if smallest == left_pathdata['cost']:
		return left_pathdata['nextPos']
	if smallest == right_pathdata['cost']:
		return right_pathdata['nextPos']
	if smallest == up_pathdata['cost']:
		return up_pathdata['nextPos']
	if smallest == down_pathdata['cost']:
		return down_pathdata['nextPos']


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


def find_our_snake(request_data):
	global snake_id
	snake_id = request_data['you']
	request_data['oursnake'] = dict()
	request_data['ourhead'] = [0, 0]
	for snake in request_data['snakes']:
		if snake['id'] == snake_id:
			request_data['ourhead'] = snake['coords'][0]
			request_data['oursnake'] = snake


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
	bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', server_Port))



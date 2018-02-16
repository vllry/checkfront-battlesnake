import copy, math
import util

def default_heatmap(width, height):
	heatmap = []
	for x in range(width):
		heatmap.append([1]*height)
	return heatmap

def fractal_heat(state, data, width, height, head_x, head_y, neck_x, neck_y, depth, factor, food_found=0):
	if depth <= 0 or factor <= 0.4: return food_found
	# This was a for x,y in [(0,1),(0,-1),(1,0),(-1,0)]:, but unrolling this was WAY faster
	food_found = heat_direction(state, data, width, height, head_x    , head_y + 1, head_x, head_y, neck_x, neck_y, depth, factor, food_found)
	food_found = heat_direction(state, data, width, height, head_x    , head_y - 1, head_x, head_y, neck_x, neck_y, depth, factor, food_found)
	food_found = heat_direction(state, data, width, height, head_x + 1, head_y,     head_x, head_y, neck_x, neck_y, depth, factor, food_found)
	food_found = heat_direction(state, data, width, height, head_x - 1, head_y,     head_x, head_y, neck_x, neck_y, depth, factor, food_found)
	return food_found

def heat_direction(state, data, width, height, new_head_x, new_head_y, head_x, head_y, neck_x, neck_y, depth, factor, food_found):
	if new_head_x == neck_x and new_head_y == neck_y:
		return food_found # not backwards
	if new_head_x < 0 or new_head_x >= width or new_head_y < 0 or new_head_y >= height:
		return food_found # stay inside the map
	if (new_head_x * 1000 + new_head_y) in state['food_cache']:
		factor *= 3
		food_found += 1
		state['food_cache'].remove(new_head_x * 1000 + new_head_y)
	data[new_head_x][new_head_y] += factor
	return fractal_heat(state, data, width, height, new_head_x, new_head_y, head_x, head_y, depth-1, factor/3, food_found)

# maxturns=11 or even 12 is possible with cython, 9 is better for regular python
def gen_heatmap(requestdata, maxturns=9, use_rings=True):
	state = copy.deepcopy(requestdata)
	width = state['width']
	height = state['height']
	final = default_heatmap(width, height)

	oursnake = state['oursnake']
	oursnakeHead = oursnake['coords'][0]
	oursnakeNeck = oursnake['coords'][1]
	oursnakeLength = len(oursnake['coords'])

	# Find the longest snake, so we can continue looping over every snake's entire torso
	longestSnakeLength = oursnakeLength
	for snake in state['snakes']:
		longestSnakeLength = max(longestSnakeLength, len(snake['coords']))

	for turn in range(1, max(maxturns+1, longestSnakeLength)):
		heatmap = default_heatmap(width, height)
		snakes = copy.deepcopy(state['snakes'])
		for snake in snakes:
			coords = snake['coords']
			# Skip parsing OUR heat (we control that) and (because this gets exponetially expensive) limit to maxturns
			food_found = 0
			if turn <= maxturns:
				state['food_cache'] = []
				for food_coords in state['food']:
					state['food_cache'].append(food_coords[0] * 1000 + food_coords[1])
				if snake['id'] != state['you']:
					# parse heat around the head
					we_are_bigger = (len(coords) < oursnakeLength)
					food_found = fractal_heat(state, heatmap, width, height, coords[0][0], coords[0][1], coords[1][0], coords[1][1], turn - we_are_bigger, (turn == 1 and 100.0 or 33.0))
				else:
					# parse heat around the head
					we_are_bigger = (len(coords) < oursnakeLength)
					food_found = fractal_heat(state, default_heatmap(width, height), width, height, coords[0][0], coords[0][1], coords[1][0], coords[1][1], turn - we_are_bigger, (turn == 1 and 100.0 or 33.0))

			# Now parse the body
			try:
				# Remove tail components that will move by the time we reach them
				tails_to_remove = turn - food_found

				for i in range(tails_to_remove): coords.pop()
			except IndexError: pass

			for x,y in coords:
				heatmap[x][y] += 700
		for x, col in enumerate(heatmap):
			for y, heat in enumerate(col):
				if heat != 1:
					if not use_rings or ((abs(x-oursnakeHead[0]) + abs(y-oursnakeHead[1])) == turn):
						final[x][y] += heat
		final[oursnakeHead[0]][oursnakeHead[1]] = 975
		final[oursnakeNeck[0]][oursnakeNeck[1]] = 950

	if 'walls' in state:
		for x,y in state['walls']:
			final[x][y] = 800

	return final


def print_heatmap(heatmap):
	text = "    Heatmap:\n"
	for y in range(len(heatmap[0])):
		for xs in heatmap:
			num = min(int(xs[y]), 999)
			if num == 1:
				text += "  - "
			else:
				text += "%3d " % num
		text += "\n"
	print text, "\n"

def test_generate(maxturns=10, print_map=False):
	test_map_data = {u'snakes': [{u'health_points': 83, u'taunt': u'', u'coords': [[2, 3], [2, 2], [1, 2], [1, 1], [1, 0], [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, 4]], u'name': u'', u'id': u'aed42e3b-57b9-4da5-9c0c-41925714b173'}, {u'health_points': 86, u'taunt': u'', u'coords': [[4, 17], [3, 17], [3, 18], [4, 18], [5, 18], [6, 18], [7, 18], [8, 18], [8, 17], [7, 17]], u'name': u'', u'id': u'aa6bc9d4-c7cd-40c1-a045-9788bf0d962c'}, {u'health_points': 65, u'taunt': u'', u'coords': [[9, 2], [10, 2], [11, 2], [12, 2], [13, 2], [13, 3], [12, 3], [11, 3], [10, 3], [9, 3], [9, 4], [10, 4], [11, 4], [12, 4], [13, 4]], u'name': u'', u'id': u'd1844ab4-48f2-4e28-acdb-325f9778ae2c'}, {u'health_points': 95, u'taunt': u'', u'coords': [[12, 12], [13, 12], [14, 12], [14, 13], [13, 13], [12, 13], [12, 14], [12, 15], [12, 16], [12, 17], [13, 17], [14, 17], [15, 17]], u'name': u'', u'id': u'ff76b2df-a959-4022-9ea2-92786b9c8d2a'}, {u'health_points': 91, u'taunt': u'', u'coords': [[18, 11], [18, 12], [17, 12], [16, 12], [15, 12], [15, 11], [15, 10], [14, 10], [13, 10], [13, 9], [14, 9], [15, 9], [16, 9], [17, 9]], u'name': u'', u'id': u'ad706415-db7d-4620-9daa-f73cb649bee2'}, {u'health_points': 80, u'taunt': u'', u'coords': [[19, 7], [19, 8], [18, 8], [18, 7], [18, 6], [18, 5], [18, 4], [18, 3], [19, 3], [19, 4], [19, 5]], u'name': u'', u'id': u'b8f1cc5c-3585-41f3-8b36-e0fa9af8126b'}, {u'health_points': 97, u'taunt': u'0xA9FF33', u'coords': [[9, 11], [8, 11], [8, 10], [7, 10], [6, 10], [6, 9], [6, 8], [6, 7], [5, 7], [5, 6], [5, 5], [5, 4], [4, 4], [3, 4], [3, 3]], u'name': u'Snakeoverflow', u'id': u'92dd5ef9-ba87-4987-882f-2511b97ec514'}], u'turn': 146, u'food': [[11, 14], [8, 3], [0, 5]], u'height': 20, u'width': 20, 'oursnake': {u'health_points': 97, u'taunt': u'0xA9FF33', u'coords': [[9, 11], [8, 11], [8, 10], [7, 10], [6, 10], [6, 9], [6, 8], [6, 7], [5, 7], [5, 6], [5, 5], [5, 4], [4, 4], [3, 4], [3, 3]], u'name': u'Snakeoverflow', u'id': u'92dd5ef9-ba87-4987-882f-2511b97ec514'}, u'dead_snakes': [], u'game_id': u'098c3eab-ea8b-4367-90d5-708ed4c49ade', u'you': u'92dd5ef9-ba87-4987-882f-2511b97ec514', 'ourhead': [9, 11]}
	heatmap = gen_heatmap(test_map_data, maxturns, True)
	if print_map:
		print_heatmap(heatmap)
